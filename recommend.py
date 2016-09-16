#!/usr/bin/env python3

import sys
from copy import deepcopy
from collections import Counter
import numpy as np
import sklearn.cluster


# Generate set of all known tags
def list_all_tags(lists_of_tags):
    all_known_tags = set()
    for list_of_tags in lists_of_tags:
        for tag in list_of_tags:
            all_known_tags.add(tag)
    return list(all_known_tags) # so it would be ordered


# Not scalable, but making hash tables for ~100 tags is an overkill
def tags_to_boolean_features(object_tags, all_known_tags):
    features = np.array( [0] * len(all_known_tags) )
    for tag in object_tags:
        try:
            features[all_known_tags.index(tag)] = 1
        except IndexError:
            pass
    return features


# Converts an index of an object feature into the tag string
def feature_index_to_tag(index, all_known_tags):
    return all_known_tags[index]


# Returns a collections.Counter object with feature indices
def count_common_tags(input_objects):
    counter = Counter()
    for obj in input_objects:
        for tag in obj:
            counter[tag] += 1
    return counter


# main
input_objects = []
tag_files = sys.argv
tag_files.pop(0)
for filename in tag_files:
    with open(filename, "r") as file:
        tags = []
        comma_delimited_tags = file.readline()
        for raw_tag in comma_delimited_tags.split(','):
            tag = raw_tag.strip()
            # Filter out artist tags because it's trivial to browse the artist manually
            if not (tag.startswith("artist:") or tag == "safe" or tag == "suggestive"):
                tags.append(tag)
        input_objects.append(tags)


all_known_tags = list_all_tags(input_objects)
feature_objects = []
for obj in input_objects:
    feature_objects.append(tags_to_boolean_features(obj, all_known_tags))

clusterer = sklearn.cluster.AffinityPropagation()
class_of_each_element = clusterer.fit_predict(np.array(feature_objects))
total_clusters = max(class_of_each_element)
print("Total clusters: " + str(total_clusters))
print(class_of_each_element)


# Returns all objects that belong to the given class number
def filter_elements_from_class(class_num, feature_objects, class_of_each_element):
    result = []
    assert(len(feature_objects) == len(class_of_each_element))
    for i in range(0, len(feature_objects)):
        if class_of_each_element[i] == class_num:
            result.append(feature_objects[i])
    return result


# Assembles the internal representation of sql-like query for each cluser of images
# The internal representation is a list of tag lists; for example:
# [ [A], [B,C] ]
# means the query is for images that have tag A and at least one of tags B and C
# It has to be converted to the syntax of a specific imageboard to be useful,
# see 'query_to_derpibooru_query' function below
def assemble_query_for_objects(input_objects, all_known_tags):
    result = []
    total_objects = len(input_objects)
    #print(total_objects)
    tag_frequencies = count_common_tags(input_objects)
    ordered_nonzero_tags = [tag for tag,frequency in tag_frequencies.most_common() if frequency > 0]
    for offset in range(0, len(ordered_nonzero_tags)):
        unprocessed_tags = ordered_nonzero_tags[offset:]
        iter_result_tags = []
        non_covered_objects = deepcopy(input_objects)
        # This loop is responsible for generating lists lists of tags with OR between them
        while len(non_covered_objects) > total_objects/6: # TUNABLE PARAMETER
            #print(len(non_covered_objects))
            # Find most common tags in objects that are not yet covered
            iter_tag_frequencies = count_common_tags(non_covered_objects)
            ordered_iter_nonzero_tags = [tag for tag,frequency in iter_tag_frequencies.most_common() if frequency > 0]
            most_common_unprocessed_tag = None
            for tag in ordered_iter_nonzero_tags:
                if tag in unprocessed_tags:
                    most_common_unprocessed_tag = tag
                    break
            else:
                return result
            #print(most_common_unprocessed_tag)
            iter_result_tags.append(most_common_unprocessed_tag)
            #print(iter_result_tags)
            objects_covered_by_tag = [obj for obj in non_covered_objects if (most_common_unprocessed_tag in obj)]
            if len(objects_covered_by_tag) == 0:
            	# cannot find any more tags to cover more of the objects 
                return result
            for obj_with_covered_tag in objects_covered_by_tag:
                non_covered_objects.remove(obj_with_covered_tag)
        if len(iter_result_tags) > 0:
            result.append(iter_result_tags)
        #print(result)
    return result


def query_to_derpibooru_query(query):
    output_string = ""
    for or_tag_list in query:
        output_string += "("
        for tag in or_tag_list:
            output_string += tag
            output_string += " || "
        output_string = output_string[:-4]
        output_string += "), "
    return output_string


# Actually invoke the magic defined above on each class
for class_num in range(0, total_clusters):
    input_objects_in_class= filter_elements_from_class(class_num, input_objects, class_of_each_element)
    top_common_tags = count_common_tags(input_objects_in_class).most_common(20)
    # Filter out small clusters in the image that don't have enough statistics to be useful
    if (top_common_tags[0][1]) <= 3: # TUNABLE PARAMETER
        continue
    #print(top_common_tags)
    query = assemble_query_for_objects(input_objects_in_class, all_known_tags)
    print(query_to_derpibooru_query(query))
    print("------")

