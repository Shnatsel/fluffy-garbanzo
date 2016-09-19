# Personal picture recommendation engine that uses your favourite pics as input

##Features:

* Accepts an unstructured set of your favourite pictures and figures out the patterns automagically
* Tag-based
  *  does not require access to gigabytes of data from other users for learning
* Outputs a tag query suitable for searching tagged imageboards
 *  does not require having the entire database locally
* Can search big amounts of data (millions of images)

## Quickstart

The engine has been tested on derpibooru; the quickstart instructions assume you're using it. Adapting it for other imageboards should be fairly trivial, see below.

 1. Install scikit-learn for Python 3. Most Linux distros have it in the repositories; non-Linux users can get it from http://scikit-learn.org/stable/
 1. Fetch the tags from the imageboard into files, one image = one file. Tags should be comma-delimited. 
  * A Linux shell script that automatically fetches tags for given images from derpibooru is included, run  `bash fetch_derpibooru_tags.sh pic1.jpg pic2.png ...` 
  * It doesn't always find a match for every image, so you might have to fall back to reverse image search to get tags for some images. Once you find the image on the board, you can get the tags in easy-to-copypaste format by appending .json to the image URL, like this: https://derpibooru.org/1253256.json
 1. Run `python3 recommend.py pic1.jpg.tags pic2.png.tags ...`

 1. The script will output several _very long_ tag queries; for derpibooru that's going to look along the lines of `(tag1 || tag2), (tag3 || tag3 || tag4), (tag2 || tag4 || tag5 || tag 7) ...` Copy the **beginning** of the query into imageboard's search box. You can usually tell when the tags become irrelevant; copy them only up to that point. Also consider sorting resulting images by score.
 1. If the results do not seem to be relevant, re-run `recommend.py` from step 2; it is currently non-deterministic and it may take several passes before it finds a really relevant tag query.

 1. If you have too few or too many results, see "Tunables" below.

## Tunables

If the program didn't work quite well the first time around (which is very likely), you can tune the following parameters at the top of recommend.py to improve the results:

1. If you have very little queries in the output and a lot of "cluster is too small to get useful results" messages, lower the `cluster_size_theshold`. It defines the minimum size of a cluster for each generating a tag query will be attempted. If you have 2-4 queries in the output you probably don't have to tune this unless you have less than 20 pictures as input.
2. If you have too many images as a result of a query - pages and pages of them that you don't feel like browsing - try increasing `cluster_coverage_allowance` a bit. Likewise, if you have too few results in the query outside of the images you supplied, consider lowering it. See also the next item, on this list...
3. Another way to tune the amount of results is choosing how much of the generated query to use. The longer the part of the query that you copy-paste into the imageboard's search box is, the more specific results you're going to get. However, method (2) on this list is the preferred way to tune this. Besides, you can generally tell when tags in the query stop being representative of what you're looking for, and asking for more unrepresentative tags is pointless.

## How it works

The script works in two principal stages.

First off it discovers classes of similar images within the input image set via sklearn's [affinity propagation](http://scikit-learn.org/stable/modules/clustering.html#affinity-propagation) clustering algorithm. This stems from the observation that people generally have several distinct favored tag combinations, and a desirable tag in one cluster would not be desirable in another (e.g. the tag "fog" is great in landscapes but is not desirable in portraits, etc).

Then, for each cluster that is big enough (there are at least `cluster_size_theshold` images in the class) it attempts to build a search query via the following algorithm:

1. Find the most common tag in the cluster (ignoring already processed tags) and mark it "selected"
2. As long as the amount of images in this cluster that _do not_ have the selected tag is greater than `cluster_size * cluster_coverage_allowance`, find the most common tag among the images not covered by and append it to the query with OR relationship.
3. Append the currently assembled tag combination delimited with OR to the output query, mark the selected tag "already processed" and go to step 1

This builds a query like `tag1 AND (tag2 OR tag3) AND (tag4 OR tag5 OR tag6) ...` for each cluster.

## Adapting this for your favourite imageboard

What the imageboard has to support for this to work:

1. Search queries such as `tag1 AND (tag2 OR tag3) AND (tag4 OR tag5 OR tag6)`. The exact syntax may vary but grouping several tags with OR relationship should be supported. For example, derpibooru/booru-on-rails engine qualifies, while danbooru does not.
2. Some form of reverse image search, e.g. by file hash, so you can find your images on the imageboard and get tags for them. If the imageboard has no reverse search, you need all your favourites to be in the form of imageboard links instead of images.

If the imageboard meets the requirements, you will have to:

1. Write a script that fetches the tags for your images from the imageboard into files. One image = one file with tags. Tags should be comma-delimited. See `fetch_derpibooru_tags.sh` for example code. (Alternatively you can just copypaste the tags for your images into files by hand, but that's gonna take a while).
2. Write a function that converts the internal representation of tag query into a valid search query for your imageboard. See functions `assemble_query_for_objects` for documentation on the internal representation and `query_to_derpibooru_query` for example code that converts it into derpibooru queries.
3. Tune the `tag_blacklist` and adapt filtering out the useless `artists:` to your imageboard's tag system (people who enjoy works of a certain artist most likely have already seen all of their works and do not need a recommendation engine to do that, so artist info is removed).

## TODO

META TODO
