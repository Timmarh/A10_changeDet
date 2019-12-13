# RWS puntenwolk visualisatie instructies

## Potree

### EPT tiles maken

#### Entwine installeren

De makkelijkste manier om entwine te installeren is via Conda. Conda is een package manager die origineel gemaakt is voor python en python bibliotheken, maar tegenwoordig voor veel meer gebruikt kan worden. Download [conda](https://docs.conda.io/en/latest/miniconda.html) en installeer. Open een anaconda prompt en voer het volgende commando uit:

```sh
conda install -c conda-forge entwine
```

#### Entwine uitvoeren

Voordat we entwine laten draaien maken we eerst een configuratie bestand aan, waarin we aangeven met welke instelling entwine moet draaien. Voor een volledige uitleg van alle opties raadpleeg [de entwine documentatie](https://entwine.io/configuration.html). De belangrijkste opties zijn:

| Naam         | Uitleg                                         |
| ------------ | ---------------------------------------------- |
| input        | Path(s) to build                               |
| output       | Output directory                               |
| srs          | Output coordinate system                       |
| reprojection | Coordinate system reprojection                 |
| scale        | Scaling factor for scaled integral coordinates |
| threads      | Number of parallel threads                     |
| schema       | Attributes to store                            |

Een typische configuratie json ziet er dan zo uit:

```json
{
    "input": "/var/data/rws/data/amsterdam/",
    "output": "/var/data/rws/data/amsterdam_ept/",
    "srs": "EPSG:28992",
    "scale": 0.001,
    "threads": 6
}
```

Hierna kunnen we entwine draaien met het configuratie bestand:

```sh
entwine build -c /path/to/config/file/
```

Zodra het proces klaar is staat het resultaat in de output folder. Dit ziet er zo uit:

```
ept-build.json
ept-data
ept-hierarchy
ept.json
ept-sources
```

Zet de output folder in de project folder onder de naam `pointcloud`.

### Potree installeren

Voor het installeren van Potree hebben we `npm` (node package manager) nodig. Deze package manager wordt automatisch geinstalleerd met `node.js`. [Download](https://nodejs.org/en/) en installeer `node.js`.

Ga naar https://github.com/potree/potree en klik op de groene `Clone or download` knop en kies `Download ZIP`. Pak de zip uit en open een command line in die directory. Voer nu de volgende commando's uit:

```sh
npm install
npm install -g gulp
npm install -g rollup
gulp build
gulp pack
```

Er is nu een `build` folder gemaakt waarin potree is gemaakt. Kopieer deze folder naar de project folder en hernoem naar `potree`.

Kopieer ook de `libs` folder naar de project folder.

### Potree app maken

In de project folder maak een index.html bestand aan:

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8" />
    <meta name="description" content="" />
    <meta name="author" content="" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no" />
    <title>Potree Viewer</title>

    <link rel="stylesheet" type="text/css" href="./potree/build/potree/potree.css" />
    <link rel="stylesheet" type="text/css" href="./potree/libs/jquery-ui/jquery-ui.min.css" />
    <link rel="stylesheet" type="text/css" href="./potree/libs/openlayers3/ol.css" />
    <link rel="stylesheet" type="text/css" href="./potree/libs/spectrum/spectrum.css" />
    <link rel="stylesheet" type="text/css" href="./potree/libs/jstree/themes/mixed/style.css" />

    <script src="./libs/jquery/jquery-3.1.1.min.js"></script>
    <script src="./libs/spectrum/spectrum.js"></script>
    <script src="./libs/jquery-ui/jquery-ui.min.js"></script>
    <script src="./libs/three.js/build/three.min.js"></script>
    <script src="./libs/other/BinaryHeap.js"></script>
    <script src="./libs/tween/tween.min.js"></script>
    <script src="./libs/d3/d3.js"></script>
    <script src="./libs/proj4/proj4.js"></script>
    <script src="./libs/openlayers3/ol.js"></script>
    <script src="./libs/i18next/i18next.js"></script>
    <script src="./libs/jstree/jstree.js"></script>
    <script src="./build/potree/potree.js"></script>
    <script src="./libs/plasio/js/laslaz.js"></script>
</head>

<body>
    <div class="potree_container" style="position: absolute; width: 100%; height: 100%; left: 0px; top: 0px; ">
        <div id="potree_render_area"></div>
        <div id="potree_sidebar_container"></div>
    </div>

    <script>
        const viewer = new Potree.Viewer(document.getElementById("potree_render_area"));

        viewer.setEDLEnabled(true);
        viewer.setFOV(60);
        viewer.setPointBudget(1 * 1000 * 1000);
        viewer.loadSettingsFromURL();

        viewer.setDescription("Text");

        viewer.loadGUI(() => {
            viewer.setLanguage("en");
            $("#menu_tools")
                .next()
                .show();
            $("#menu_clipping")
                .next()
                .show();
            viewer.toggleSidebar();
        });

        Potree.loadPointCloud(
            "pointcloud/ept.json",
            "naamPuntenwolk",
            e => {
                viewer.scene.addPointCloud(e.pointcloud);

                viewer.fitToScreen();
            }
        );
    </script>  
</body>

</html>
```

### App serveren

Om de app te kunnen openen in de browser moeten we de bestanden serveren via http. Hiervoor gebruiken we een webserver. In productie raden we aan om Apache of Nginx te gebruiken. Tijdens het testen kan het handiger zijn om de `http-server` library te gebruiken die je met `npm` kan installeren:

```sh
npm install -g http-server
```

Ga nu naar de project folder en daar open een command line:

```sh
http-server -p 8000
```

Open een browser en ga naar `http://localhost:8000`.

Als alles goed is gegaan wordt Potree nu geopend en de puntenwolk ingeladen.
