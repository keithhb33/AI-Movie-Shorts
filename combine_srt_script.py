import re
import argparse

def normalize_text(text):
    # Remove punctuation, newlines, and extra spaces; convert to lowercase
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def is_all_caps(text):
    # Check if the text is in all caps
    return text.isupper()

def read_and_normalize_file(file_path, exclude_single_words=True):
    
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    normalized_lines = [
        (line, normalize_text(line)) 
        for line in lines 
        if not is_all_caps(line.strip())
    ]
    for i in range(len(normalized_lines)):
        # Extract the current tuple
        current_tuple = normalized_lines[i]
        # Create a new tuple with the modified second value
        new_tuple = (
            current_tuple[0],
            current_tuple[1].replace('–', '-').replace('“', '"').replace("’", "").replace('”', "")
        )
        # Replace the old tuple with the new one
        normalized_lines[i] = new_tuple
    if exclude_single_words:
        normalized_lines = [
            (line, norm_line) 
            for line, norm_line in normalized_lines 
            if len(norm_line.split()) > 1
        ]
    return normalized_lines

def similar_enough(a, b, allowed_differences=1):
    words_a = a.split()
    words_b = b.split()
    if len(words_a) > 4 and len(words_b) > 4:
        common_words = set(words_a).intersection(set(words_b))
        total_words = max(len(words_a), len(words_b))
        differences = total_words - len(common_words)
        return differences <= allowed_differences
    return a == b

def find_matching_lines(file1_lines, file2_lines):
    matching_lines = []
    used_time_ranges = []
    
    for line, normalized_line in file1_lines:
        matched = False
        for idx, (time_range, norm_line2) in enumerate(file2_lines):
            if similar_enough(normalized_line, norm_line2) and (time_range not in used_time_ranges):
                matching_lines.append((time_range, line.strip()))
                used_time_ranges.append(time_range)
                matched = True
                break
        if not matched:
            matching_lines.append((None, line.strip()))
    return matching_lines

def read_and_normalize_srt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin1') as file:
            content = file.read()
    # Split by subtitle blocks
    blocks = re.split(r'\n\s*\d+\s*\n', content)
    srt_lines = []
    for block in blocks:
        if '-->' in block:
            parts = block.split('\n')
            time_range = parts[0].strip()
            lines = parts[1:]
            for line in lines:
                if line.strip():
                    normalized_line = normalize_text(line)
                    srt_lines.append((time_range, normalized_line))
    return srt_lines

def main():
    parser = argparse.ArgumentParser(description='Process a movie script and SRT file.')
    parser.add_argument('movie_title', type=str, help='The title of the movie')

    args = parser.parse_args()
    movie_title = args.movie_title
    
    file1_path = f'scripts/srt_files/{movie_title}_summary.txt'
    file2_path = f'scripts/srt_files/{movie_title}_modified.srt'
    output_path = f'scripts/srt_files/{movie_title}_combined.txt'
    
    # Read and normalize the files
    file1_lines = read_and_normalize_file(file1_path)
    file2_lines = read_and_normalize_srt(file2_path)
    
    # Find matching lines
    matching_lines = find_matching_lines(file1_lines, file2_lines)
    print("MATCHING LINES: " + str(matching_lines))
    
    # Write matching lines with time ranges to the output file
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write("0\n")  # Write a 0 at the beginning of the file
        last_time_end = None
        for time_range, line in matching_lines:
            if time_range and ' --> ' in time_range:
                start_time, end_time = time_range.split(' --> ')
                if last_time_end:
                    output_file.write(f"{last_time_end}\n")
                output_file.write(f"{start_time}\n{line}\n")
                last_time_end = end_time
            else:
                output_file.write(f"{line}\n")
        if last_time_end:
            output_file.write(f"{last_time_end}\n")

if __name__ == '__main__':
    main()
