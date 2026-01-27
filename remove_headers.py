#!/usr/bin/env python3
"""
Script to remove YAML front matter headers from all markdown files.
The header is the section between the first pair of '---' delimiters at the beginning of the file.
"""
import os
import sys


def remove_header_from_markdown(filepath):
    """Remove YAML front matter from a markdown file."""
    print(f"Processing: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  Error reading file: {e}")
        return False
    
    # Check if file starts with YAML front matter (---)
    if not content.startswith('---'):
        print(f"  No header found, skipping")
        return True
    
    # Find the end of the header (second ---)
    try:
        # Split by --- to find the header section
        parts = content.split('---', 2)
        
        if len(parts) < 3:
            print(f"  Warning: Malformed header (no closing ---), skipping")
            return False
        
        # parts[0] is empty (before first ---)
        # parts[1] is the header content
        # parts[2] is the body content after the header
        
        # Get the body content (after the header)
        body = parts[2].lstrip('\n')
        
        # Write back only the body content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(body)
        
        print(f"  ✓ Header removed successfully")
        return True
        
    except Exception as e:
        print(f"  Error processing file: {e}")
        return False


def main():
    """Main function to process all markdown files."""
    # Find all markdown files
    md_files = []
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and .git
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                md_files.append(filepath)
    
    print(f"Found {len(md_files)} markdown files\n")
    
    if not md_files:
        print("No markdown files found!")
        return 0
    
    processed = 0
    success = 0
    
    for filepath in md_files:
        if remove_header_from_markdown(filepath):
            success += 1
        processed += 1
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total files processed: {processed}")
    print(f"  Successfully processed: {success}")
    print(f"  Failed: {processed - success}")
    print(f"{'='*60}")
    
    return 0 if success == processed else 1


if __name__ == '__main__':
    sys.exit(main())
