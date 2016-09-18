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

 1. Fetch the tags from the imageboard into files, one image = one file. Tags should be comma-delimited. 
  * A Linux shell script that automatically fetches tags for given images from derpibooru is included, run  `bash fetch_derpibooru_tags.sh pic1.jpg pic2.png ...` 
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

TODO

## Adapting this for your favourite imageboard

TODO

## TODO

META TODO