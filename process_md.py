#!/usr/bin/env python3
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime
import yaml


def get_git_date(filepath):
    """Get the last modified date from git log for a file."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ad", "--", filepath],
            capture_output=True,
            text=True,
            check=True,
        )
        if result.stdout.strip():
            # Parse git date and convert to YYYY-MM-DD format
            git_date = result.stdout.strip()
            # Convert to datetime object and format as YYYY-MM-DD
            dt = datetime.strptime(git_date, "%a %b %d %H:%M:%S %Y %z")
            return dt.strftime("%Y-%m-%d")
        return None
    except subprocess.CalledProcessError:
        return None


def infer_metadata_from_content(content, filepath):
    """Infer title, description, tags, and categories from content."""
    lines = content.split("\n")

    # Extract title from first heading or filename
    title = None
    for line in lines:
        line = line.strip()
        if line.startswith("# "):
            title = line[2:].strip()
            break

    if not title:
        # Use filename as fallback
        title = Path(filepath).stem.replace("-", " ").replace("_", " ").title()

    # Extract description from first paragraph after header or from heading
    description = ""
    in_header = False
    header_ended = False

    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not in_header:
                in_header = True
            else:
                header_ended = True
                continue

        if in_header and not header_ended:
            continue

        if header_ended or not in_header:
            if line.strip() and not line.startswith("#"):
                # First non-heading, non-empty line
                description = line.strip()[:150]  # Limit description length
                if len(description) == 150:
                    description += "..."
                break

    # If no description found, use a generic one
    if not description:
        description = f"Technical documentation about {title.lower()}"

    # Infer categories from directory structure
    filepath_obj = Path(filepath)
    categories = []

    # Get directory parts (excluding leading '.' if relative path)
    parts = [p for p in filepath_obj.parts if p != "." and p != ".."]
    if parts:
        # Use first directory as category, limit to max 12 characters
        category = parts[0][:12]
        categories = [category]

    # Infer tags from content and filename
    tags = set()

    # Add category as tag
    if categories:
        tags.add(categories[0])

    # Extract potential tags from filename and content
    filename = filepath_obj.stem.lower()
    content_lower = content.lower()

    # Common tech terms to look for
    tech_keywords = [
        "docker",
        "python",
        "redis",
        "mysql",
        "database",
        "networking",
        "ssh",
        "vpn",
        "kvm",
        "virtualization",
        "linux",
        "arch",
        "ubuntu",
        "nginx",
        "apache",
        "ssl",
        "tls",
        "dns",
        "proxy",
        "cloudflare",
        "frappe",
        "react",
        "native",
        "mobile",
        "api",
        "rest",
        "json",
        "yaml",
        "bash",
        "shell",
        "script",
        "automation",
        "devops",
        "security",
        "firewall",
        "ssl",
        "certificate",
        "backup",
        "restore",
    ]

    for keyword in tech_keywords:
        if keyword in filename or keyword in content_lower:
            tags.add(keyword)

    # Remove category from tags if it's already there (to avoid duplication)
    if categories and categories[0] in tags:
        tags.remove(categories[0])

    tags_list = sorted(list(tags))

    # Limit to maximum 5 tags (point 9)
    if len(tags_list) > 5:
        tags_list = tags_list[:5]

    return title, description, tags_list, categories


def has_duplicate_headers(content):
    """Check if content has duplicate YAML headers (not counting horizontal rules)."""
    lines = content.split("\n")
    yaml_headers = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if line == "---":
            # Check if this is a header block (has YAML-like content after it)
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # If next line looks like YAML (contains colons, title, date, etc.)
                if any(
                    key in next_line.lower()
                    for key in [
                        "title:",
                        "date:",
                        "description:",
                        "tags:",
                        "categories:",
                        "permalink:",
                    ]
                ):
                    # This is a YAML header
                    yaml_headers.append(i)
                    # Skip to find its end
                    j = i + 1
                    while j < len(lines) and lines[j].strip() != "---":
                        j += 1
                    if j < len(lines):
                        yaml_headers.append(j)  # End of header
                    i = j + 1
                else:
                    # This is likely a horizontal rule, skip it
                    i += 1
            else:
                i += 1
        else:
            i += 1

    # Return True if more than one complete header found
    return len(yaml_headers) > 2


def parse_existing_header(content):
    """Parse existing YAML header if present."""
    if not content.startswith("---"):
        return None, content

    try:
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None, content

        header_yaml = parts[1]
        body = parts[2].lstrip("\n")

        header = yaml.safe_load(header_yaml)
        return header, body
    except (yaml.YAMLError, IndexError):
        return None, content


def create_header(title, date, description, tags, categories):
    """Create YAML header."""
    header = {
        "title": title,
        "date": date,
        "description": description,
        "permalink": f"posts/{{{{ title | slug }}}}/index.html",
        "tags": tags,
        "categories": categories,
    }

    yaml_str = yaml.dump(header, default_flow_style=False, sort_keys=False)
    # Remove quotes from keys that don't need them
    yaml_str = re.sub(
        r"'(title|date|description|permalink|tags|categories)':", r"\1:", yaml_str
    )

    return f"---\n{yaml_str}---\n\n"


def process_markdown_file(filepath):
    """Process a single markdown file."""
    print(f"Processing: {filepath}")

    # Get git date
    git_date = get_git_date(filepath)
    if not git_date:
        print(f"  Warning: Could not get git date for {filepath}")
        return False

    # Read file content
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  Error reading file: {e}")
        return False

    # Check for duplicate headers
    if has_duplicate_headers(content):
        print(f"  Warning: Found duplicate headers in {filepath}")
        # Remove duplicate headers, keep only the first one
        lines = content.split("\n")
        new_lines = []
        header_found = False
        i = 0

        while i < len(lines):
            line = lines[i]
            if line.strip() == "---" and not header_found:
                # First header - keep it
                new_lines.append(line)
                i += 1
                # Find end of first header
                while i < len(lines) and lines[i].strip() != "---":
                    new_lines.append(lines[i])
                    i += 1
                if i < len(lines):
                    new_lines.append(lines[i])  # Add closing ---
                i += 1
                header_found = True
            elif line.strip() == "---" and header_found:
                # Potential duplicate header - check if it's really a header
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if any(
                        key in next_line.lower()
                        for key in [
                            "title:",
                            "date:",
                            "description:",
                            "tags:",
                            "categories:",
                            "permalink:",
                        ]
                    ):
                        # This is a duplicate header, skip it
                        print(f"  Removing duplicate header starting at line {i + 1}")
                        i += 1
                        # Skip until the end of this duplicate header
                        while i < len(lines) and lines[i].strip() != "---":
                            i += 1
                        if i < len(lines):
                            i += 1  # Skip the closing ---
                        continue
                # Not a duplicate header, keep it as content
                new_lines.append(line)
                i += 1
            else:
                new_lines.append(line)
                i += 1

        content = "\n".join(new_lines)

        # Write back the cleaned content
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  Fixed duplicate headers")
        except Exception as e:
            print(f"  Error writing cleaned file: {e}")
            return False

    # Parse existing header
    existing_header, body = parse_existing_header(content)

    # Infer metadata from content
    inferred_title, inferred_description, inferred_tags, inferred_categories = (
        infer_metadata_from_content(body or content, filepath)
    )

    if existing_header:
        # Update existing header
        updated = False

        # Update date
        if existing_header.get("date") != git_date:
            existing_header["date"] = git_date
            updated = True

        # Add missing categories or truncate existing ones exceeding 12 chars
        existing_cats = existing_header.get("categories")
        if not existing_cats and inferred_categories:
            existing_header["categories"] = inferred_categories
            updated = True
        elif existing_cats and inferred_categories:
            # Check if any existing category exceeds 12 characters
            new_cats = []
            for cat in existing_cats:
                if len(cat) > 12:
                    new_cats.append(cat[:12])
                    updated = True
                else:
                    new_cats.append(cat)
            if updated:
                existing_header["categories"] = new_cats

        # Limit existing tags to maximum 5 (point 9)
        existing_tags = existing_header.get("tags")
        if existing_tags and len(existing_tags) > 5:
            existing_header["tags"] = existing_tags[:5]
            updated = True

        if updated:
            # Recreate header with updated values
            new_header = create_header(
                existing_header.get("title", inferred_title),
                existing_header.get("date", git_date),
                existing_header.get("description", inferred_description),
                existing_header.get("tags", inferred_tags),
                existing_header.get("categories", inferred_categories),
            )

            new_content = new_header + body

            # Write back to file
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"  Updated header with new date and/or categories")
                return True
            except Exception as e:
                print(f"  Error writing file: {e}")
                return False
        else:
            print(f"  No updates needed")
            return True
    else:
        # Create new header
        new_header = create_header(
            inferred_title,
            git_date,
            inferred_description,
            inferred_tags,
            inferred_categories,
        )

        new_content = new_header + content

        # Write back to file
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"  Added new header")
            return True
        except Exception as e:
            print(f"  Error writing file: {e}")
            return False


def main():
    """Main function to process all markdown files."""
    # Find all markdown files
    md_files = []
    for root, dirs, files in os.walk("."):
        # Skip hidden directories and .git
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                md_files.append(filepath)

    print(f"Found {len(md_files)} markdown files")

    processed = 0
    updated = 0

    for filepath in md_files:
        processed += 1
        if process_markdown_file(filepath):
            updated += 1

    print(f"\nSummary:")
    print(f"  Total files processed: {processed}")
    print(f"  Files updated: {updated}")


if __name__ == "__main__":
    main()
