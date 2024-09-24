import sys
import os
import hashlib
import struct
import subprocess
import collections


dm_single_close_quote = u'\u2019' # unicode
dm_double_close_quote = u'\u201d'
END_TOKENS = ['.', '!', '?', '...', "'", "`", '"', dm_single_close_quote, dm_double_close_quote, ")"] # acceptable ways to end a sentence

all_train = "cnndm_new/cnndm_used_for_source_target/train" #Path to the train dataset
all_val = "cnndm_new/cnndm_used_for_source_target/val"  #Path to the validate dataset
all_test = "cnndm_new/cnndm_used_for_source_target/test"  #Path to the test dataset

files_dir = "cnndm_new/cnndm_source_target" #Path to the source target file
# These are the number of .story files we expect there to be in dir_path and dm_stories_dir



def read_text_file(text_file):
  lines = []
  with open(text_file, "r", encoding="utf-8") as f:
    for line in f:
      lines.append(line.strip())
  return lines


def hashhex(s):
  """Returns a heximal formated SHA1 hash of the input string."""
  h = hashlib.sha1()
  h.update(s.encode())
  return h.hexdigest()


def get_url_hashes(url_list):
  return [hashhex(url) for url in url_list]


def fix_missing_period(line):
  """Adds a period to a line that is missing a period"""
  if '@highlight' in line: return line
  if line=="": return line
  if line[-1] in END_TOKENS: return line
  # print line[-1]
  return line + " ."


def get_art_abs(story_file):
  lines = read_text_file(story_file)

  # Put periods on the ends of lines that are missing them (this is a problem in the dataset because many image captions don't end in periods; consequently they end up in the body of the article as run-on sentences)
  lines = [fix_missing_period(line) for line in lines]

  # Separate out article and abstract sentences
  article_lines = []
  highlights = []
  next_is_highlight = False
  for idx,line in enumerate(lines):
    if line == "":
      continue # empty line
    elif line.startswith("@highlight"):
      next_is_highlight = True
    elif next_is_highlight:
      highlights.append(line)
    else:
      article_lines.append(line)

  # Make article into a single string
  article = ' '.join(article_lines)

  # Make abstract into a signle string
  abstract = ' '.join(highlights)

  return article, abstract


def write_to_bin(dir_path, out_prefix):
  count=0
  """Reads the .story files corresponding to the urls listed in the url_file and writes them to a out_file."""
  print("Making bin file for URLs listed in %s..." % dir_path)
  story_fnames = os.listdir(dir_path)
  with open(out_prefix + '.source', 'wt', encoding="utf-8") as source_file, open(out_prefix + '.target', 'wt',encoding="utf-8") as target_file:
    for idx,s in enumerate(story_fnames):
      # Look in the story dirs to find the .story file corresponding to this ur
      count=count+1
      if os.path.isfile(os.path.join(dir_path, s)):
        print(count)
        story_file = os.path.join(dir_path, s)
      else:
        print("Error: Couldn't find story file %s in either story directories %s and %s." % (s, dir_path))
        # Check again if stories directories contain correct number of files
        # print("Checking that the stories directories %s and %s contain correct number of files..." % (dir_path, dm_stories_dir))
        # check_num_stories(dir_path, num_expected_cnn_stories)
        # check_num_stories(dm_stories_dir, num_expected_dm_stories)
        # raise Exception("Stories directories %s and %s contain correct number of files but story file %s found in neither." % (dir_path, dm_stories_dir, s))

      # Get the strings to write to .bin file
      article, abstract = get_art_abs(story_file)

      # Write article and abstract to files
      source_file.write(article + '\n')
      target_file.write(abstract + '\n')

  print("Finished writing files")


def check_num_stories(stories_dir, num_expected):
  num_stories = len(os.listdir(stories_dir))
  if num_stories != num_expected:
    raise Exception("stories directory %s contains %i files but should contain %i" % (stories_dir, num_stories, num_expected))


if __name__ == '__main__':
  # Check the stories directories contain the correct number of .story files

  # Create some new directories
  if not os.path.exists(files_dir): os.makedirs(files_dir)

  # Read the stories, do a little postprocessing then write to bin files
  write_to_bin(all_test, os.path.join(files_dir, "test"))
  write_to_bin(all_val, os.path.join(files_dir, "val"))
  write_to_bin(all_train, os.path.join(files_dir, "train"))