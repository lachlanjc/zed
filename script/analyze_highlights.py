from collections import defaultdict
from pathlib import Path
import argparse
import re

# Initialize a regular expression to match @ instances
pattern = re.compile(r'(@[a-zA-Z_.]+)')

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Analyze highlight.scm files for unique instances and their languages.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Include a list of languages for each tag.')
    return parser.parse_args()

def find_highlight_files(root_dir):
    """Find all highlight.scm files within a specified root directory."""
    for path in Path(root_dir).rglob('highlights.scm'):
        yield path

def count_instances(files):
    """Count all unique instances of @{name} and their languages in the given files."""
    # Use a defaultdict to automatically handle keys that aren't yet in the dictionary
    instances = defaultdict(lambda: {'count': 0, 'languages': set()})
    for file_path in files:
        # Correctly identify the language by getting the directory name one level up
        language = file_path.parent.name
        with open(file_path, "r") as file:
            text = file.read()
            matches = pattern.findall(text)
            for match in matches:
                instances[match]['count'] += 1
                instances[match]['languages'].add(language)
    return instances

def print_instances(instances, verbose=False):
    """Print the instances along with count and, if verbose, languages."""
    for item, details in sorted(instances.items(), key=lambda x: x[0]):
        languages = ', '.join(sorted(details['languages']))
        if verbose:
            print(f"{item} ({details['count']}) - [{languages}]")
        else:
            print(f"{item} ({details['count']})")

def main():
    args = parse_arguments()

    base_dir = Path(__file__).parent.parent
    core_path = base_dir / 'crates/languages/src'
    extension_path = base_dir / 'extensions/astro/languages'

    core_instances = count_instances(find_highlight_files(core_path))
    extension_instances = count_instances(find_highlight_files(extension_path))

    # Determine instances unique to extensions
    unique_extension_instances = {k: v for k, v in extension_instances.items() if k not in core_instances}

    # Print shared and extension-only instances
    print('Shared:\n')
    print_instances(core_instances, args.verbose)

    if unique_extension_instances:
        print('\nExtension-only:\n')
        print_instances(unique_extension_instances, args.verbose)

if __name__ == '__main__':
    main()
