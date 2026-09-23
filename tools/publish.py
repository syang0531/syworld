# -*- coding: utf-8 -*-
"""Checks and uploads a SY World release to CurseForge.

    python tools/publish.py 1.0.0 --dry-run     # check only (no token needed)
    python tools/publish.py 1.0.0               # check, then upload (needs CURSEFORGE_TOKEN)
    python tools/publish.py 1.0.0 --changelog   # print that version's CHANGELOG section
    python tools/publish.py 1.0.0 --path        # print that version's export, e.g. pack/SY World-1.0.0.zip

The pack itself is made by the CurseForge App and exported into pack/ - CurseForge's moderation
rules require the App's format and forbid editing the manifest it writes. So this script never
builds or edits a pack: it finds the export whose manifest says <version>, checks it, and sends it
as it is. Standard library only, so it runs the same on a laptop and in GitHub Actions.

Checks, before anything is sent:
  - exactly one pack/*.zip has manifest.json "version" == <version> and "name" == pack.json name
  - the manifest targets pack.json's Minecraft version and a NeoForge loader
  - every mod in pack.json's "family" is in the manifest (a new SY mod is added there first)
  - CHANGELOG.md has a "## <version>" section (it becomes the CurseForge changelog)
"""
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://minecraft.curseforge.com/api'


def fail(message):
    print('FAIL: ' + message)
    sys.exit(1)


def load_config():
    with open(os.path.join(ROOT, 'pack.json'), encoding='utf-8') as f:
        return json.load(f)


def changelog_section(version):
    with open(os.path.join(ROOT, 'CHANGELOG.md'), encoding='utf-8') as f:
        lines = f.read().splitlines()
    out, inside = [], False
    for line in lines:
        if line.startswith('## '):
            if inside:
                break
            inside = line[3:].strip() == version
            continue
        if inside:
            out.append(line)
    text = '\n'.join(out).strip()
    if not text:
        fail('CHANGELOG.md has no "## %s" section' % version)
    return text


def find_pack(config, version):
    pack_dir = os.path.join(ROOT, 'pack')
    matches = []
    for name in sorted(os.listdir(pack_dir)) if os.path.isdir(pack_dir) else []:
        if not name.lower().endswith('.zip'):
            continue
        path = os.path.join(pack_dir, name)
        try:
            with zipfile.ZipFile(path) as z:
                manifest = json.loads(z.read('manifest.json'))
        except (KeyError, zipfile.BadZipFile, json.JSONDecodeError) as e:
            print('  skip %s: not a CurseForge export (%s)' % (name, e))
            continue
        if manifest.get('version') == version:
            matches.append((path, manifest))
    if not matches:
        fail('no pack/*.zip with manifest version %s - export it from the CurseForge App into pack/' % version)
    if len(matches) > 1:
        fail('more than one export says version %s: %s' % (version, ', '.join(os.path.basename(p) for p, _ in matches)))
    return matches[0]


def check_manifest(config, manifest):
    if manifest.get('name') != config['name']:
        fail('manifest name is %r, expected %r' % (manifest.get('name'), config['name']))
    mc = manifest.get('minecraft', {})
    if mc.get('version') != config['minecraft_version']:
        fail('manifest targets Minecraft %r, expected %r' % (mc.get('version'), config['minecraft_version']))
    loaders = [l.get('id', '') for l in mc.get('modLoaders', [])]
    if not any(l.startswith(config['loader'] + '-') for l in loaders):
        fail('manifest has no %s loader (found %s)' % (config['loader'], loaders))
    in_pack = {f.get('projectID') for f in manifest.get('files', [])}
    missing = [m['name'] for m in config['family'] if m['curseforge_project_id'] not in in_pack]
    if missing:
        fail('these SY mods are not in the pack: ' + ', '.join(missing))
    extra = sorted(in_pack - {m['curseforge_project_id'] for m in config['family']})
    return loaders, len(in_pack), extra


def request(method, url, token, body=None, content_type=None):
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header('X-Api-Token', token)
    req.add_header('User-Agent', 'syworld-publish')
    if content_type:
        req.add_header('Content-Type', content_type)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        fail('%s %s -> HTTP %s: %s' % (method, url, e.code, e.read().decode('utf-8', 'replace')))


def minecraft_version_id(token, version):
    """CurseForge wants game version ids, not names. Minecraft versions live in the version types
    whose slug starts with "minecraft" (one type per major line)."""
    types = request('GET', API + '/game/version-types', token)
    mc_types = {t['id'] for t in types if t.get('slug', '').startswith('minecraft')}
    ids = [v['id'] for v in request('GET', API + '/game/versions', token)
           if v.get('gameVersionTypeID') in mc_types and v.get('name') == version]
    if not ids:
        fail('CurseForge has no Minecraft game version named %r' % version)
    return ids[0]


def upload(config, token, path, version, changelog, release_type):
    project = config['curseforge_project_id']
    if not project:
        fail('pack.json curseforge_project_id is 0 - create the CurseForge project first')
    metadata = {
        'changelog': changelog,
        'changelogType': 'markdown',
        'displayName': '%s %s' % (config['name'], version),
        'gameVersions': [minecraft_version_id(token, config['minecraft_version'])],
        'releaseType': release_type,
    }
    boundary = uuid.uuid4().hex
    with open(path, 'rb') as f:
        data = f.read()
    parts = [
        ('--%s\r\nContent-Disposition: form-data; name="metadata"\r\n'
         'Content-Type: application/json\r\n\r\n' % boundary).encode() + json.dumps(metadata).encode() + b'\r\n',
        ('--%s\r\nContent-Disposition: form-data; name="file"; filename="%s"\r\n'
         'Content-Type: application/zip\r\n\r\n' % (boundary, os.path.basename(path))).encode() + data + b'\r\n',
        ('--%s--\r\n' % boundary).encode(),
    ]
    result = request('POST', '%s/projects/%s/upload-file' % (API, project), token,
                     b''.join(parts), 'multipart/form-data; boundary=' + boundary)
    print('uploaded: CurseForge file id %s' % result.get('id'))


def main():
    # The changelog is Korean with em dashes; a Korean Windows console defaults to cp949 and cannot
    # print them. UTF-8 always, so --changelog works locally and when redirected to a file.
    sys.stdout.reconfigure(encoding='utf-8')
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = {a for a in sys.argv[1:] if a.startswith('--')}
    if len(args) != 1:
        print(__doc__)
        sys.exit(2)
    version = args[0].lstrip('v')
    config = load_config()

    if '--changelog' in flags:
        print(changelog_section(version))
        return

    if '--path' in flags:
        print(os.path.relpath(find_pack(config, version)[0], ROOT).replace(os.sep, '/'))
        return

    changelog = changelog_section(version)
    path, manifest = find_pack(config, version)
    loaders, count, extra = check_manifest(config, manifest)
    print('pack      : %s' % os.path.relpath(path, ROOT))
    print('manifest  : %s %s, Minecraft %s, %s' % (manifest['name'], manifest['version'],
                                                  manifest['minecraft']['version'], ', '.join(loaders)))
    print('mods      : %d (all %d SY mods present%s)' % (count, len(config['family']),
                                                         ', plus project ids %s' % extra if extra else ''))
    print('changelog : %d lines' % len(changelog.splitlines()))

    if '--dry-run' in flags:
        print('dry run: nothing uploaded')
        return
    token = os.environ.get('CURSEFORGE_TOKEN', '').strip()
    if not token:
        fail('CURSEFORGE_TOKEN is empty')
    upload(config, token, path, version, changelog, os.environ.get('RELEASE_TYPE', 'release'))


if __name__ == '__main__':
    main()
