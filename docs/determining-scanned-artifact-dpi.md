# Determining scanned artifact DPI

Given a scanned page of sheet music:

https://www.digitalniknihovna.cz/mzk/view/uuid:5c5a6d8c-b434-4496-a9ac-67d518230273?page=uuid:1d321a19-70c9-4c43-a168-e32b4436804e

Go to the end and find the page with the calibration table:

<img src="https://api.kramerius.mzk.cz/search/iiif/uuid:9a47a0d2-8129-4812-8f18-2734f1b791d2/full/pct:20/0/default.jpg" />

Each calibration table has slightly different dimensions - see the list of known tables at the end of this document.

Measure the size of a known landmark on the calibration table in pixels and convert that to DPI:

```
MILLIMETERS_IN_INCH = 24.4

DPI = (size_in_pixels / size_in_millimeters) * 24.4
```

If the calibration table is missing, I would:

- compare staff height to known pieces if they seem similar
- else compare notehead size

Staff heights:

```
Handwritten (mm):
8.161379310344827
8.329655172413792
8.903859649122808
8.989473684210525
```

Notehead sizes (square):

```
Typeset (mm):
1.9691228070175437
2.054736842105263
2.140350877192982

Handwritten (mm):
1.766896551724138
1.8510344827586205
1.8835087719298245
2.019310344827586
```


## Known calibration tables


### Datacolor, Spyder Checkr 24

<img src="https://api.kramerius.mzk.cz/search/iiif/uuid:9a47a0d2-8129-4812-8f18-2734f1b791d2/540,2835,2359,1691/pct:20/0/default.jpg" />

Official page:
https://www.datacolor.com/spyder/products/spyder-checkr-24/

Dimensions from:
https://www.foto-erhardt.com/accessories/other-photo-accessories/calibration/datacolor-spydercheckr-24_technik.html

Outer dimensions are 140x200 millimeters.

I computed the square patch to be exactly 26.5 millimeters on each side.

Computing the square dimensions:

```
Shorter side:
200mm ~ 2307px => 281.45400 DPI
200mm ~ 2325px => 283.65 DPI

Longer side:
140mm ~ 1640px => 285.828571 DPI
140mm ~ 1635px => 284.957142 DPI

Conclude with 285 DPI

Square:
309px => 26.4mm
311px => 26.6mm

Conclude with 26.5mm
```


## X-rite, ColorChecker Classic

<img src="https://api.kramerius.mzk.cz/search/iiif/uuid:9d1060c5-0a8b-4ca1-a4fb-8d2a5c666448/115,8,3508,2494/pct:20/0/default.jpg" />

Contains a 50 millimeter ruler in the bottom right corner.

One square has 40.5 millimeters on each side.

This DOES NOT allign with the dimension listed on the wikipedia page (51mm), which means we cannot assume the dimensions to be standardized. https://en.wikipedia.org/wiki/ColorChecker


## X-rite ColorChecker (mini)

<img src="https://api.kramerius.mzk.cz/search/iiif/uuid:e986cc92-72f6-4cfe-8317-c764d627aa4b/967,2666,2029,1503/pct:40/0/default.jpg" />

Contains a 50 millimeter ruler on the side.
