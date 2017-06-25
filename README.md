# Sequence to sequence Chinese word segmenation (CWS) post-editing

## Require
#### Python 2.7x

## Usage 

```
python cws_postediting.py --ori=<original inputfile> --seg=<segmented inputfile> --out=<post-editing outputfile>
```

## Example

Files in `test_data/` are examples.
```
test_data/
  ├── original_input.txt
  ├── segmented.txt
  └── out.txt
```
`original_input.txt` is an example of original input file.

`segmentent.txt` is an example of segmented file containing tranlsations errors.

`out.txt` the output file of post-editing.

To see the testing case, please run 
```
python cws_postediting.py
```
or
```
python cws_postediting.py 
--ori=./test_data/original_input.txt \
--seg=./test_data/segmented.txt \ 
--out=./test_data/out.txt
```
