"""Manual isolated validation; the real pipeline always tests its own candidate."""
import json
import os
import subprocess
import sys
from upstream import published_release,tag_revision,release_identity

release=published_release()
tag=release['tag_name']
if release['draft'] or release['prerelease']:raise ValueError('Expected a stable published release')
sha=tag_revision(tag);version,image=release_identity(tag,sha)
env={**os.environ,'LAZYCAT_SOURCE_TAG':tag,'LAZYCAT_SOURCE_REVISION':sha,'LAZYCAT_SOURCE_VERSION':version,
    'LAZYCAT_APPLICATION_VERSION':version,'LAZYCAT_OUTPUT_IMAGE':image}
subprocess.run([sys.executable,'-B','scripts/verify_runtime.py'],env=env,check=True)
