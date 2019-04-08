# Code Explanation

## Core Running Flow

![](http://cdn.marklux.cn/20190408001320.png)

## XML Document reference

sample (a full data set example is given at `data.xml`):

```
<wheathers>
    <wheather id="1" prob="0.44">
        <general>
            <position>ThePalaceMuseum</position>
            <district>DongCheng</district>
            <date>20181116</date>
            <type>windy</type>
            <city>BeiJing</city>
            <windDirection>S</windDirection>
            <temperature>14.44</temperature>
            <windForce>4.33</windForce>
            <humidity>0.53</humidity>
        </general>
        <spatioTemporal>
            <space x="116.403414" y="39.924091" />
            <time x="0" y="2" />
        </spatioTemporal>
    </wheather>
    ...
</wheathers>
```

We use a node `<wheather>` to model a wheather forecast information.

Explanation for tags & attributes

- `id`

    the index identifier for the node, we use this to locate a node.

- `prob`

    the fuzzy probablity of node, in situation of wheather forecast, it suggests the information's accuracy.
    
    notice that all the attribute share this probablity together.

- `general`

    this tag contains all the general attributes (numerical & categorical)

- `spatioTemporal`

    this tag contains the spatio attribute and temporal attribute

    in our case, all the spatiotemporal value can represent in format of tuple `[x,y]`

## How we run the expirement

1. Dump weather forecast data from source website and convert it into XML Docuement, put it into `SOURCE_FILE_PATH` (definded in `settings.py`)

2. Run `process.py`

3. After process, a navigation tree would be returned, for instance:

    ```
    |_[root]() -> 360
        |_[district](DongCheng) -> 360
            |_[position](MingChengWallRuinsPark) -> 60
            |  |_[type](windy) -> 27 [u'449', u'443'...]
            |  |_[type](sunny) -> 33
            |_[position](TempleOfConfucius) -> 60
            |  |_[type](windy) -> 37
            |  |_[type](sunny) -> 23
            |_[position](LamaTemple) -> 60
            |  |_[type](windy) -> 27
            |  |_[type](sunny) -> 33
            |_[position](TheImperialCollege) -> 60
            |  |_[type](windy) -> 26
            |  |_[type](sunny) -> 34
            |_[position](ThePalaceMuseum) -> 60
            |  |_[type](windy) -> 32
            |  |_[type](sunny) -> 28
            |_[position](TheTempleOfHeaven) -> 60
                |_[type](windy) -> 34
                |_[type](sunny) -> 26
    ```

    for each leaf node, an id list is returned to locate the real data node in data set.

4.  As we get the navigation tree, we can get the relevant tuples.

    Then we can calculate the required metrics (recall, precision, F-Score & Ecost)