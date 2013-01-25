from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.management.base import BaseCommand
from django.utils.datastructures import SortedDict
import os
from ...manifests import ConfiguredStaticFilesManifest


class Command(BaseCommand):
    help = 'Creates a file that maps static file names to their URLs.'

    def handle(self, *args, **options):
        found_files = SortedDict()
        manifest = ConfiguredStaticFilesManifest()
        manifest.clear()

        for finder in finders.get_finders():
            for path, storage in finder.list([]):
                # Prefix the relative path if the source storage contains it
                if getattr(storage, 'prefix', None):
                    prefixed_path = os.path.join(storage.prefix, path)
                else:
                    prefixed_path = path

                if prefixed_path not in found_files:
                    found_files[prefixed_path] = (storage, path)

        for storage, path in found_files.values():
            try:
                generate_url = staticfiles_storage.generate_url
            except AttributeError:
                raise AttributeError('%s doesn\'t define a generate_url method.'
                        ' Did you remember to extend StaticManifestMixin?')
            hashed_name = generate_url(path)
            manifest.add(path, hashed_name)

        manifest.flush()
