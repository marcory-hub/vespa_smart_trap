
**One-line purpose:** detection of qr code on hornet, main index [[example_vespatraps]]
**Short summary:** Interactive leaflet map to track the location of the nest. Each tag can be individually selected on the map to see the flying distance with a circle for each hornet.
**Agent:** archived

---

https://www.instructables.com/AIIoT-Yellow-Legged-Asian-Hornet-Nest-Localizer/


[![AI/IoT Yellow Legged Asian Hornet Nest Localizer](https://content.instructables.com/FOM/ZZ51/LX39PE2H/FOMZZ51LX39PE2H.jpg?auto=webp&frame=1&width=525&height=1024&fit=bounds&md=MjAyNC0wNi0wNyAwNTozMjo0My4w)](https://content.instructables.com/FOM/ZZ51/LX39PE2H/FOMZZ51LX39PE2H.jpg?auto=webp&frame=1&width=1024&height=1024&fit=bounds&md=MjAyNC0wNi0wNyAwNTozMjo0My4w)

[![AI/IoT Yellow Legged Asian Hornet Nest Localizer](https://content.instructables.com/FPS/62U9/LX39PE1M/FPS62U9LX39PE1M.jpg?auto=webp&frame=1&width=210&height=1024&fit=bounds&md=MjAyNC0wNi0wNyAwNTozMTo1OS4w)](https://content.instructables.com/FPS/62U9/LX39PE1M/FPS62U9LX39PE1M.jpg?auto=webp&frame=1&width=1024&height=1024&fit=bounds&md=MjAyNC0wNi0wNyAwNTozMTo1OS4w)

[![AI/IoT Yellow Legged Asian Hornet Nest Localizer](https://content.instructables.com/FEC/LUDN/LX39PE20/FECLUDNLX39PE20.jpg?auto=webp&frame=1&width=210&height=1024&fit=bounds&md=MjAyNC0wNi0wNyAwNTozMjowMi4w)](https://content.instructables.com/FEC/LUDN/LX39PE20/FECLUDNLX39PE20.jpg?auto=webp&frame=1&width=1024&height=1024&fit=bounds&md=MjAyNC0wNi0wNyAwNTozMjowMi4w)

[![AI/IoT Yellow Legged Asian Hornet Nest Localizer](https://content.instructables.com/FXB/E4JG/LX39PE3L/FXBE4JGLX39PE3L.png?auto=webp&frame=1&crop=3:2&width=210&fit=bounds&md=MjAyNC0wNi0wNyAwNTozNzozMS4w)](https://content.instructables.com/FXB/E4JG/LX39PE3L/FXBE4JGLX39PE3L.png?auto=webp&frame=1&width=1024&fit=bounds&md=MjAyNC0wNi0wNyAwNTozNzozMS4w)

The Asian Hornet (Vespa velutina) is invasive to our nature! As an intern at [Makerspace 'De Nayer'](http://www.makerspacedenayer.be/), i have done some research and with the help of the manager, [Davy](https://www.instructables.com/member/davy/) designed an AI, IoT and/or machine vision device to pinpoint the nests of the Asian hornet.

  

### Features:

- Interactive leaflet map to track the location of the nest.
- Each tag can be individually selected on the map to see the flying distance with a circle for each hornet.
- esp32 web server.
- MySQL database.
- PHP for accessing the data from the database.
- 3D printable model.
- WAMP server to run the database or if you have the possibilty, online (phpmyadmin, mysql)

## Supplies

- **Microcontroller:** NodeMCU-ESP32 (Joy-It)
- **Ai Camera/sensor:** Huskylens
- **Camera:** 2MP OV2640 (Because the camera of the HuskyLens needs to be positioned at an angle and the focus needs to be adjusted, we attach a separate camera to the HuskyLens. Make sure that the camera type is with a threaded barrel lens.)
- A jar to hold the attractant (Jars tested with succes on the 3D model: Bonne Maman, Andros, Doritos, Monoprix, Carrefour, Jardin Bio, Planète Bio, etc.)
- 2x M3x6 bolts
- 6x M3x10 bolts (countersunk) or 6x 3x10 screws (countersunk)
- plexiglass (acrylic) rectangle (19mm x 38mm x 2mm)
- 3D Printed parts

## Step 1: Before You Start

[![Before You Start](https://content.instructables.com/FU1/P65Q/LX0EWR80/FU1P65QLX0EWR80.jpg?auto=webp&frame=1&width=966&height=1024&fit=bounds&md=MjAyNC0wNi0wNSAwNDoyOToxNS4w)](https://content.instructables.com/FU1/P65Q/LX0EWR80/FU1P65QLX0EWR80.jpg?auto=webp&frame=1&width=1024&height=1024&fit=bounds&md=MjAyNC0wNi0wNSAwNDoyOToxNS4w)

[![Before You Start](https://content.instructables.com/FFL/RWQI/LX39PD57/FFLRWQILX39PD57.png?auto=webp&frame=1&crop=3:2&width=234&fit=bounds&md=MjAyNC0wNi0wNyAwMDo0Nzo1Ni4w)](https://content.instructables.com/FFL/RWQI/LX39PD57/FFLRWQILX39PD57.png?auto=webp&frame=1&fit=bounds&md=MjAyNC0wNi0wNyAwMDo0Nzo1Ni4w)

[![Before You Start](https://content.instructables.com/FWR/4CXS/LX4P58TD/FWR4CXSLX4P58TD.jpg?auto=webp&frame=1&width=234&height=1024&fit=bounds&md=MjAyNC0wNi0wNyAwODo0NToxMi4w)](https://content.instructables.com/FWR/4CXS/LX4P58TD/FWR4CXSLX4P58TD.jpg?auto=webp&frame=1&width=1024&height=1024&fit=bounds&md=MjAyNC0wNi0wNyAwODo0NToxMi4w)

[![Before You Start](https://content.instructables.com/FR6/S7ZA/LXX9YGXP/FR6S7ZALXX9YGXP.jpg?auto=webp&frame=1&width=234&height=1024&fit=bounds&md=MjAyNC0wNi0yNyAxMzowMjozOC4w)](https://content.instructables.com/FR6/S7ZA/LXX9YGXP/FR6S7ZALXX9YGXP.jpg?auto=webp&frame=1&width=1024&height=1024&fit=bounds&md=MjAyNC0wNi0yNyAxMzowMjozOC4w)

**3D Print settings**

The 3D files can be found on [Makerworld](https://makerworld.com/en/models/509427), [Printables](https://www.printables.com/model/903068-aiiot-yellow-legged-asian-hornet-nest-localizer) or [Thingiverse](https://www.thingiverse.com/thing:6673371).

It's recommended to print all the parts with a layer height of 0.2mm. (I used 10-15% infill)

You only need some support for the "Middle part" the other parts can be printed without supports.

we used PLA for the prototype, but it may be recommended to print with PETG, ABS or ASA.

**Learn April Tags**

These are the AprilTags that you need to teach the HuskyLens. Make them small enough to fit on the back of the hornet. Connect the red wire from the HuskyLens to the VIN pin on the ESP32 and the black wire to the GND pin to power the HuskyLens. Now, we can learn the AprilTags to the HuskyLens. Short press the "Learning" button to learn the specified tag. The tags can be glued to the hornet's back with a drop of wood glue between the wings as shown. Don't cut too close to the tag, ensure there is still a small white border around the outside of the AprilTag.

**Learn insects (Posibility)**

Long press the "Learning button" to continuously learn the specified insect from different angles and distances. This function is heavily reliant on the dataset it was trained on, which means there's a possibility it may not perform optimally.

## Step 2: WAMP Server Installation

[![WAMP Server Installation](https://content.instructables.com/FRX/AWDE/LX0ETLWK/FRXAWDELX0ETLWK.png?auto=webp&frame=1&crop=3:2&width=600&fit=bounds&md=MjAyNC0wNi0wNCAwNjozNDozNS4w)](https://content.instructables.com/FRX/AWDE/LX0ETLWK/FRXAWDELX0ETLWK.png?auto=webp&frame=1&width=1024&fit=bounds&md=MjAyNC0wNi0wNCAwNjozNDozNS4w)

[![WAMP Server Installation](https://content.instructables.com/F3R/SI1Z/LX39PD5X/F3RSI1ZLX39PD5X.png?auto=webp&frame=1&crop=3:2&width=600&fit=bounds&md=MjAyNC0wNi0wNyAwMDo1MDowMy4w)](https://content.instructables.com/F3R/SI1Z/LX39PD5X/F3RSI1ZLX39PD5X.png?auto=webp&frame=1&width=1024&fit=bounds&md=MjAyNC0wNi0wNyAwMDo1MDowMy4w)

**Step 1:** For installing a WAMP (Windows, Apache, MySQL, and PHP) server to run the database I followed the video above.

**Step 2 Accessing MyPhpAdmin:** After completing the instructions for installing the WAMP server, you should be able to navigate to the server via the Google address bar by searching "localhost" You should see a page similar to the one above. Go to "Your Aliases" and click on PhpMyAdmin to add the database. The username is "root" with an empty password.

**Step 3 Make the database:** Make sure that the structure from the database is the same as shown in the picture.

**Step 4 Add user and password:** Go to "User Accounts," then "Add User Account." Choose a username and password (write them down). Scroll down to "Global Privileges" and check all. Once everything is done, press "Go."

**Step 5:** Go to the "www" directory on your PC from the WAMP server and create a new file as shown in the video. Copy and paste the code below into this new PHP file. Change the user, password, and database name at line 41 with the ones you created in step 4.This is the code for the map that shows the different circles for each hornet.

**Step 6:** We initialize the map and set its view to the chosen geographic coordinates. To do this, we need to set the coordinates where the map will be centered. Change the 'SetViewCoordinates' to the coordinates of the area near where the traps are located (line 114 in the code, put it between the [ ] like this: [51.068356, 4.498862]). Ensure that these coordinates are not the same as where the trap(s) are placed.

  

<!DOCTYPE html>  
<html lang="en">  
<head>  
    <meta charset="UTF-8">  
    <meta name="viewport" content="width=device-width, initial-scale=1.0">  
    <title>Hornet map</title>  
      
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />  
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>  
    <style>  
        #map {  
            height: 725px;  
            width: 100%;  
        }  
        .control-box {  
            position: absolute;  
            top: 10px;  
            right: 10px;  
            background: white;  
            padding: 10px;  
            border: 1px solid #ccc;  
            z-index: 1000;  
        }  
    </style>  
</head>  
<body>  
    <div id="map"></div>  
      
    <div class="control-box">  
        <input type="checkbox" id="tags" name="selection" value="tags">  
        <label for="tags">Tags</label>  
        <input type="checkbox" id="insect" name="selection" value="insect">  
        <label for="insect">Insect</label>  
        <div id="identSelection" style="display:none;">  
            <h3>Selecteer Insect</h3>  
            <div id="checkboxes"></div>  
        </div>  
    </div>  
      
    <?php  
    $mysqli = new mysqli("localhost", "User", "Password", "DatabaseName");  
  
  
    // Check connection  
    if ($mysqli->connect_errno) {  
        echo "Failed to connect to MySQL: " . $mysqli->connect_error;  
        exit();  
    }  
  
  
    // Initialize associative arrays to store data grouped by ident  
    $data_by_ident_hornet = array();  
    $data_by_ident_insect = array();  
  
  
    // Perform query for hornet data  
    if ($result = $mysqli->query("SELECT ident, locatie, tijd FROM detector WHERE reserve ='1'")) {  
        if ($result->num_rows > 0) {  
            while ($row = $result->fetch_assoc()) {  
                $data_by_ident_hornet[$row["ident"]][] = array("locatie" => $row["locatie"], "tijd" => $row["tijd"]);  
            }  
        }  
        $result->free_result();  
    } else {  
        echo "Error executing the hornet query: " . $mysqli->error;  
    }  
  
  
    // Perform query for insect data  
    if ($result = $mysqli->query("SELECT ident, locatie, tijd FROM detector WHERE reserve ='2'")) {  
        if ($result->num_rows > 0) {  
            while ($row = $result->fetch_assoc()) {  
                $data_by_ident_insect[$row["ident"]][] = array("locatie" => $row["locatie"], "tijd" => $row["tijd"]);  
            }  
        }  
        $result->free_result();  
    } else {  
        echo "Error executing the insect query: " . $mysqli->error;  
    }  
  
  
    $mysqli->close();  
  
  
    // Associative array to map insect IDs to names  
    $insect_names = array(  
        "1" => "Asian hornet",  
        "2" => "European hornet",  
        "3" => "French wasp",  
        "4" => "Common wasp"  
    );  
    ?>  
      
    <script>  
        function rainbow(numOfSteps, step) {  
            var r, g, b;  
            var h = step / numOfSteps;  
            var i = ~~(h * 6);  
            var f = h * 6 - i;  
            var q = 1 - f;  
            switch(i % 6){  
                case 0: r = 1; g = f; b = 0; break;  
                case 1: r = q; g = 1; b = 0; break;  
                case 2: r = 0; g = 1; b = f; break;  
                case 3: r = 0; g = q; b = 1; break;  
                case 4: r = f; g = 0; b = 1; break;  
                case 5: r = 1; g = 0; b = q; break;  
            }  
            var c = "#" + ("00" + (~ ~(r * 255)).toString(16)).slice(-2) + ("00" + (~ ~(g * 255)).toString(16)).slice(-2) + ("00" + (~ ~(b * 255)).toString(16)).slice(-2);  
            return (c);  
        }  
  
  
        var identColors = {};  
        var colorIndex = 0;  
  
  
        function calculateRadius(time) {   
            return time;  
        }  
  
  
        var map = L.map('map').setView([SetVieuwCoordinates], 13);  
  
  
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {  
            maxZoom: 19,  
            attribution: '© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'  
        }).addTo(map);  
  
  
        var circles = {};  
        var insectCircles = {};  
  
  
        function toggleCircles(circles, show) {  
            for (var ident in circles) {  
                circles[ident].forEach(function(circle) {  
                    if (show) {  
                        circle.addTo(map);  
                    } else {  
                        map.removeLayer(circle);  
                    }  
                });  
            }  
        }  
  
  
        function toggleIdentSelection(display) {  
            document.getElementById('identSelection').style.display = display ? 'block' : 'none';  
        }  
  
  
        function updateSelectionLabels(isTags) {  
        var headerText = isTags ? 'Selecteer Tag' : 'Selecteer Insect';  
        document.getElementById('identSelection').getElementsByTagName('h3')[0].textContent = headerText;  
    }  
  
  
    document.getElementById('tags').addEventListener('change', function() {  
        if (this.checked) {  
            document.getElementById('insect').disabled = true;  
            toggleIdentSelection(true);  
            updateCheckboxes(circles, true); // Voor tags  
            updateSelectionLabels(true);  
        } else {  
            document.getElementById('insect').disabled = false;  
            toggleIdentSelection(false);  
            toggleCircles(circles, false);  
            clearCheckboxes();  
            updateSelectionLabels(false);  
        }  
    });  
  
  
    document.getElementById('insect').addEventListener('change', function() {  
        if (this.checked) {  
            document.getElementById('tags').disabled = true;  
            toggleIdentSelection(true);  
            updateCheckboxes(insectCircles, false); // Voor insecten  
            updateSelectionLabels(false);  
        } else {  
            document.getElementById('tags').disabled = false;  
            toggleIdentSelection(false);  
            toggleCircles(insectCircles, false);  
            clearCheckboxes();  
            updateSelectionLabels(true);  
        }  
    });  
  
  
        function updateCheckboxes(circles, isTags) {  
            var container = document.getElementById('checkboxes');  
            container.innerHTML = '';  
            for (var ident in circles) {  
                var checkbox = document.createElement('input');  
                checkbox.type = 'checkbox';  
                checkbox.id = 'checkbox-' + ident;  
                checkbox.onchange = function() {  
                    var ident = this.id.replace('checkbox-', '');  
                    toggleCircles({[ident]: circles[ident]}, this.checked);  
                };  
                var label = document.createElement('label');  
                label.htmlFor = 'checkbox-' + ident;  
                  
                // If it is for tags, add "Ident: number"; otherwise, add only the name of the insect.  
                if (isTags) {  
                    label.appendChild(document.createTextNode('Ident: ' + ident));  
                } else {  
                    label.appendChild(document.createTextNode(getInsectName(ident)));  
                }  
                  
                container.appendChild(checkbox);  
                container.appendChild(label);  
                container.appendChild(document.createElement('br'));  
            }  
        }  
  
  
        function clearCheckboxes() {  
            var container = document.getElementById('checkboxes');  
            container.innerHTML = '';  
        }  
  
  
        // Function to get insect name from ID  
        function getInsectName(ident) {  
            // Associative array mapping IDs to names  
            var insectNames = <?php echo json_encode($insect_names); ?>;  
            return insectNames[ident] || 'Insect ' + ident; // If name not found, default to "Insect {ID}"  
        }  
  
  
        <?php foreach ($data_by_ident_hornet as $ident => $data) { ?>  
            if (!identColors.hasOwnProperty(<?php echo json_encode($ident); ?>)) {  
                identColors[<?php echo json_encode($ident); ?>] = colorIndex++;  
            }  
              
            circles[<?php echo json_encode($ident); ?>] = [];  
              
            <?php foreach ($data as $item) { ?>  
                var locatie = <?php echo json_encode(explode(",", $item["locatie"])); ?>;  
                var tijd = <?php echo $item["tijd"]; ?>;  
                var radius = calculateRadius(tijd);  
                var color = rainbow(16, identColors[<?php echo json_encode($ident); ?>]);  
                var circle = L.circle([parseFloat(locatie[0]), parseFloat(locatie[1])], {  
                    color: '#000',  
                    fillColor: color,  
                    fillOpacity: 0.2,  
                    radius: radius  
                });  
                circles[<?php echo json_encode($ident); ?>].push(circle);  
            <?php } ?>  
        <?php } ?>  
  
  
        <?php foreach ($data_by_ident_insect as $ident => $data) { ?>  
            if (!identColors.hasOwnProperty(<?php echo json_encode($ident); ?>)) {  
                identColors[<?php echo json_encode($ident); ?>] = colorIndex++;  
            }  
              
            insectCircles[<?php echo json_encode($ident); ?>] = [];  
              
            <?php foreach ($data as $item) { ?>  
                var locatie = <?php echo json_encode(explode(",", $item["locatie"])); ?>;  
                var tijd = <?php echo $item["tijd"]; ?>;  
                var radius = calculateRadius(tijd);  
                var color = rainbow(16, identColors[<?php echo json_encode($ident); ?>]);  
                var circle = L.circle([parseFloat(locatie[0]), parseFloat(locatie[1])], {  
                    color: '#000',  
                    fillColor: color,  
                    fillOpacity: 0.2,  
                    radius: radius  
                });  
                insectCircles[<?php echo json_encode($ident); ?>].push(circle);  
          
            <?php } ?>  
        <?php } ?>  
    </script>  
</body>  
</html>  

  

**Step 3:** Follow the same steps for this code: create a new PHP file, copy and paste the code, then change the User, Password, and DatabaseName. This code is used for inserting data into the database.
```
<?php  
$servername = "localhost";  
$username = "User";  
$password = "Password";  
$dbname = "DatabaseName";  
  
  
// Create connection  
$conn = new mysqli($servername, $username, $password, $dbname);  
// Check connection  
if ($conn->connect_error) {  
    die("Connection failed: " . $conn->connect_error);  
}  
echo 'Connection successful<br/>';    
$x = 1;  
  
  
if(!empty($_REQUEST['hoornaar'])){  
       $hoornaar = $_REQUEST['hoornaar'];  
       echo "Hornet detected: ".$hoornaar;  
       echo '<br/>';    
}  
  
  
if(!empty($_REQUEST['ident'])){  
       $ident = $_REQUEST['ident'];  
       echo "Identification hornet: ".$ident;  
       echo '<br/>';    
  
  
}  
if(!empty($_REQUEST['locatie'])){  
    $locatie = $_REQUEST['locatie'];  
    echo "Location detector: ".$locatie;  
    echo '<br/>';    
  
  
}  
if(!empty($_REQUEST['tijd'])){  
    $tijd = $_REQUEST['tijd'];  
    echo "time away from nest: ".$tijd;  
    echo '<br/>';    
  
  
}  
  
  
if(!empty($_REQUEST['reserve'])){  
    $reserve = $_REQUEST['reserve'];  
    echo "reserve: ".$reserve;  
    echo '<br/>';    
  
  
}  
  
  
if( $hoornaar == "1"){  
$sql = "INSERT INTO detector (volgnummer, timestamp, hornet, ident, locatie, tijd, reserve) VALUES (NULL, current_timestamp(),'".$hoornaar."', '".$ident."','".$locatie."','".$tijd."','".$reserve."')";  
    if ($conn->query($sql) === TRUE) {  
        echo "New record created successfully";  
    } else {  
        echo "Error: " . $sql . "<br>" . $conn->error;  
    }  
}  
$conn->close();  
echo 'The End<br/>';    
?>  

## Step 3: Uploading Code to Esp32

[![Uploading Code to Esp32](https://content.instructables.com/FBG/FJL5/LXRK6OJR/FBGFJL5LXRK6OJR.png?auto=webp&frame=1&fit=bounds&md=MjAyNC0wNi0yMyAwNjo1NDoyNC4w)](https://content.instructables.com/FBG/FJL5/LXRK6OJR/FBGFJL5LXRK6OJR.png?auto=webp&frame=1&fit=bounds&md=MjAyNC0wNi0yMyAwNjo1NDoyNC4w)

**UPLOADING CODE:**

Because we use SPIFFS to run the web server on the ESP32, we need an older version of the Arduino IDE (I used 1.8.18). It doesn't work with the newer version of Arduino IDE2.0

Download the codes and put them in a folder (**rename this folder to "hornetsV12.3"**) as shown in the picture. Make sure to create an additional folder inside this folder named "data". Open the first code named "hornetsV12.3.ino". The other codes should automatically open in different tabs inside the Arduino IDE.

When using a WAMP server, you need to change the "YourIPaddress" in the Arduino "**hornetsV12.3**" code to your PC's IP address at line 101 and 143 in the serverName string. If the line numbers aren't visible, go to **File > Preferences** and select **"Display line numbers."**

If you don't know how to find your PC's IP address, check this [link](https://support.microsoft.com/en-gb/windows/find-your-ip-address-in-windows-f21a9bbc-c582-55cd-35e0-73431160a1b9) for Windows.

It's possible to change how many tags you want to detect by changing the value of the variable maxTags on line 34. It's default value is 4 and can go up to 16.

After this is done you can upload the code to the esp32.

### Attachments

- [![download {{ file.name }}](https://www.instructables.com/assets/img/pixel.png)hornetsV12.3.ino](https://content.instructables.com/FC8/U7IL/LXRK6OGJ/FC8U7ILLXRK6OGJ.ino)
    
    [Download](https://content.instructables.com/FC8/U7IL/LXRK6OGJ/FC8U7ILLXRK6OGJ.ino)
    
- [![download {{ file.name }}](https://www.instructables.com/assets/img/pixel.png)Processor_functions.ino](https://content.instructables.com/FOC/1870/LXRK6OGK/FOC1870LXRK6OGK.ino)
    
    [Download](https://content.instructables.com/FOC/1870/LXRK6OGK/FOC1870LXRK6OGK.ino)
    
- [![download {{ file.name }}](https://www.instructables.com/assets/img/pixel.png)Server_requests.ino](https://content.instructables.com/FST/M5DY/LXRK6OH4/FSTM5DYLXRK6OH4.ino)
    
    [Download](https://content.instructables.com/FST/M5DY/LXRK6OH4/FSTM5DYLXRK6OH4.ino)
    
- [![download {{ file.name }}](https://www.instructables.com/assets/img/pixel.png)SPIFFS_manager.ino](https://content.instructables.com/FNJ/Q6G0/LXRK6OHP/FNJQ6G0LXRK6OHP.ino)
    
    [Download](https://content.instructables.com/FNJ/Q6G0/LXRK6OHP/FNJQ6G0LXRK6OHP.ino)
    
- [![download {{ file.name }}](https://www.instructables.com/assets/img/pixel.png)WiFi.ino](https://content.instructables.com/F2D/89QP/LXRK6OIB/F2D89QPLXRK6OIB.ino)
    
    [Download](https://content.instructables.com/F2D/89QP/LXRK6OIB/F2D89QPLXRK6OIB.ino)
    

## Step 4: Installing the SPIFFS Filesystem

**Installing the Arduino ESP32 filesystem uploader in windows:**

**Step 1:** Follow these steps to install the filesystem for the SPIFFS:

[Install ESP32 Filesystem Uploader in Arduino IDE | Random Nerd Tutorials](https://randomnerdtutorials.com/install-esp32-filesystem-uploader-arduino-ide/)

**Step 2:** To upload the SPIFFS, it's necessary to put these two HTML files into the "data" folder we just created in Step 3. Open an empty Notepad file, copy and paste the first code, and save it as "index2.html" in the "data" folder. Do the same with the second code, save it as "wifimanager.html", and the 3rd code, save it as "styleWIFI.css" and place them in the "data" folder.

**Note:** The filenames should match exactly as they are written.

**Step 3 upload the SPIFFS:** To upload the SPIFFS, go to **Tools >****ESP32 Sketch Data Upload**.

First code: index2.html

<!DOCTYPE html>  
<html>  
<head>  
  <title>ESP32 Web Server For Hornets</title>  
  <meta name="viewport" content="width=device-width, initial-scale=1">  
  <link rel="icon" href="data:,">  
  <style>  
    body {  
      font-family: 'Arial', sans-serif;  
      background-color: #f2f2f2;  
      color: #333;  
      text-align: center;  
      margin: 0;  
      padding: 0;  
      display: flex;  
      flex-direction: column;  
      align-items: center;  
      justify-content: center;  
      min-height: 100vh;  
    }  
    h1 {  
      color: #000;  
      font-size: 2.5rem;  
      text-shadow: 4px 4px 8px rgba(0, 0, 0, 0.3);  
      margin-top: 20px 0;  
    }  
    p {  
      font-size: 1.6rem;  
      color: #555;  
      text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);  
      margin: 10px 0;  
    }  
    .button-container {  
      display: flex;  
      justify-content: center;  
      align-items: center;  
      gap: 20px;  
    }  
    .button {  
      background: linear-gradient(135deg, #ff6b6b, #ff3d00);  
      border: none;  
      border-radius: 50px;  
      color: #fff;  
      padding: 24px 48px;  
      text-decoration: none;  
      font-size: 1.6rem;  
      cursor: pointer;  
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);  
      transition: background 0.3s ease, transform 0.2s ease;  
    }  
    .button:hover {  
      background: linear-gradient(135deg, #ff3d00, #ff6b6b);  
      transform: scale(1.1);  
    }  
    .button2 {  
      background: linear-gradient(135deg, #2bcbba, #45a6e5);  
    }  
    .container {  
      background-color: rgba(255, 255, 255, 0.9);  
      padding: 40px;  
      border-radius: 16px;  
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);  
      text-align: center;  
    }  
    .icon {  
      font-size: 3rem;  
    }  
    /* Opmaak voor coördinaten */  
    th, td {  
      padding: 10px;  
      border-bottom: 1px solid #ccc;  
      text-align: center;  
    }  
        
    button#submit {  
      margin-top: 20px;  
      background-color: #34B249;  
      color: #fff;  
      border: none;  
      border-radius: 5px;  
      padding: 10px 20px;  
      font-size: 1.4rem;  
      cursor: pointer;  
      transition: background-color 0.3s ease;  
    }  
    button#submit:hover {  
      background-color: #32CD32;  
    }  
  </style>  
</head>  
<body>  
<div class="container">  
    <h1>Control Center For Hornets</h1>  
    <div class="button-container">  
      <a href="/object"><button class="button">OBJECT</button></a>  
      <a href="/tags"><button class="button button2">TAGS</button></a>  
    </div>  
    <br>  
    <p>Algorithm: <strong>%ALGORITHM%</strong></p>  
   </div>  
   <br>   
  <div class="container">  
    <fieldset>  
      <legend>WGS84 coordinates only!</legend>  
      <div id="spacer_20"></div>  
      <form method="GET" action="/save">  
        <table>  
          <tr>  
            <th>Example(51.068356,4.498862)</th>  
            <td>%COORDINATES%</td>  
            <td>%AREA%</td>  
          </tr>  
        </table>  
        <button id="submit" type="submit" value="save" onclick="return validateForm()">Save</button>  
      </form>  
    </fieldset>  
  </div>  
</body>  
</html>   

If you want to use an LED, use this index instead:

<!DOCTYPE html>  
<html>  
<head>  
  <title>ESP32 Web Server For Hornets</title>  
  <meta name="viewport" content="width=device-width, initial-scale=1">  
  <link rel="icon" href="data:,">  
  <link rel="stylesheet" type="text/css" href="style.css">  
  <style>  
    body {  
      font-family: 'Arial', sans-serif;  
      background-color: #f2f2f2;  
      color: #333;  
      text-align: center;  
      margin: 0;  
      padding: 0;  
      display: flex;  
      flex-direction: column;  
      align-items: center;  
      justify-content: center;  
      min-height: 100vh;  
    }  
    h1 {  
      color: #000;  
      font-size: 2.5rem;  
      text-shadow: 4px 4px 8px rgba(0, 0, 0, 0.3);  
      margin-top: 20px 0;  
    }  
    p {  
      font-size: 1.6rem;  
      color: #555;  
      text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);  
      margin: 10px 0;  
    }  
    .button-container {  
      display: flex;  
      justify-content: center;  
      align-items: center;  
      gap: 20px;  
    }  
    .button {  
      background: linear-gradient(135deg, #ff6b6b, #ff3d00);  
      border: none;  
      border-radius: 50px;  
      color: #fff;  
      padding: 24px 48px;  
      text-decoration: none;  
      font-size: 1.6rem;  
      cursor: pointer;  
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);  
      transition: background 0.3s ease, transform 0.2s ease;  
    }  
    .button:hover {  
      background: linear-gradient(135deg, #ff3d00, #ff6b6b);  
      transform: scale(1.1);  
    }  
    .button2 {  
      background: linear-gradient(135deg, #2bcbba, #45a6e5);  
    }  
    .container {  
      background-color: rgba(255, 255, 255, 0.9);  
      padding: 40px;  
      border-radius: 16px;  
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);  
      text-align: center;  
    }  
    .icon {  
      font-size: 3rem;  
    }  
      
    th, td {  
      padding: 10px;  
      border-bottom: 1px solid #ccc;  
      text-align: center;  
    }  
        
    button#submit {  
      margin-top: 20px;  
      background-color: #34B249;  
      color: #fff;  
      border: none;  
      border-radius: 5px;  
      padding: 10px 20px;  
      font-size: 1.4rem;  
      cursor: pointer;  
      transition: background-color 0.3s ease;  
    }  
    button#submit:hover {  
      background-color: #32CD32;  
    }  
  </style>  
</head>  
<body>  
<div class="container">  
    <h1>Control Center For Hornets</h1>  
    <div class="button-container">  
      <a href="/object"><button class="button">OBJECT</button></a>  
      <a href="/tags"><button class="button button2">TAGS</button></a>  
    </div>  
    <p>Algorithm: <strong>%ALGORITHM%</strong></p>  
    <br>  
    <div class="button-container">  
      <a href="/on"><button class="button">ON</button></a>  
      <a href="/off"><button class="button button2">OFF</button></a>  
    </div>  
    <br>  
    <p>LED state: <strong> %STATE%</strong></p>  
   </div>  
   <br>   
  <div class="container">  
    <fieldset>  
      <legend>WGS84 coordinates only!</legend>  
      <div id="spacer_20"></div>  
      <form method="GET" action="/save">  
        <table>  
          <tr>  
            <th>Example(51.068356,4.498862)</th>  
            <td>%COORDINATES%</td>  
            <td>%AREA%</td>  
          </tr>  
        </table>  
        <button id="submit" type="submit" value="save" onclick="return validateForm()">Save</button>  
      </form>  
    </fieldset>  
  </div>  
</body>  
</html>  

Second code: wifimanager.html

<!DOCTYPE html>  
<html>  
<head>  
  <title>ESP Wi-Fi Manager</title>  
  <meta name="viewport" content="width=device-width, initial-scale=1">  
  <link rel="icon" href="data:,">  
  <link rel="stylesheet" type="text/css" href="styleWIFI.css">  
</head>  
<body>  
  <div class="topnav">  
    <h1>ESP Wi-Fi Manager</h1>  
  </div>  
  <div class="content">  
    <div class="card-grid">  
      <div class="card">  
        <form action="/" method="POST">  
          <p>  
            <label for="ssid">SSID</label>  
            <input type="text" id ="ssid" name="ssid"><br>  
            <label for="pass">Password</label>  
            <input type="text" id ="pass" name="pass"><br>  
            <input type ="submit" value ="Submit">  
          </p>  
        </form>  
      </div>  
    </div>  
  </div>  
</body>  
</html>  

3rd code: styleWIFI.css

html {  
  font-family: Arial, Helvetica, sans-serif;   
  display: inline-block;   
  text-align: center;  
}  
  
  
h1 {  
  font-size: 1.8rem;   
  color: white;  
}  
  
  
p {   
  font-size: 1.4rem;  
}  
  
  
.topnav {   
  overflow: hidden;   
  background-color: #0A1128;  
}  
  
  
body {    
  margin: 0;  
}  
  
  
.content {   
  padding: 5%;  
}  
  
  
.card-grid {   
  max-width: 800px;   
  margin: 0 auto;   
  display: grid;   
  grid-gap: 2rem;   
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));  
}  
  
  
.card {   
  background-color: white;   
  box-shadow: 2px 2px 12px 1px rgba(140,140,140,.5);  
}  
  
  
.card-title {   
  font-size: 1.2rem;  
  font-weight: bold;  
  color: #034078  
}  
  
  
input[type=submit] {  
  border: none;  
  color: #FEFCFB;  
  background-color: #034078;  
  padding: 15px 15px;  
  text-align: center;  
  text-decoration: none;  
  display: inline-block;  
  font-size: 16px;  
  width: 100px;  
  margin-right: 10px;  
  border-radius: 4px;  
  transition-duration: 0.4s;  
  }  
  
  
input[type=submit]:hover {  
  background-color: #1282A2;  
}  
  
  
input[type=text], input[type=number], select {  
  width: 50%;  
  padding: 12px 20px;  
  margin: 18px;  
  display: inline-block;  
  border: 1px solid #ccc;  
  border-radius: 4px;  
  box-sizing: border-box;  
}  
  
  
label {  
  font-size: 1.2rem;   
}  
.value{  
  font-size: 1.2rem;  
  color: #1282A2;    
}  
.state {  
  font-size: 1.2rem;  
  color: #1282A2;  
}  
button {  
  border: none;  
  color: #FEFCFB;  
  padding: 15px 32px;  
  text-align: center;  
  font-size: 16px;  
  width: 100px;  
  border-radius: 4px;  
  transition-duration: 0.4s;  
}  
.button-on {  
  background-color: #034078;  
}  
.button-on:hover {  
  background-color: #1282A2;  
}  
.button-off {  
  background-color: #858585;  
}  
.button-off:hover {  
  background-color: #252524;  
}   

## Step 5: Assembling the Base

[![Assembling the Base](https://content.instructables.com/F38/QW6S/LWW4HWQS/F38QW6SLWW4HWQS.jpg?auto=webp&frame=1&width=800&height=1024&fit=bounds&md=MjAyNC0wNi0wMSAwNzowODo1Mi4w)](https://content.instructables.com/F38/QW6S/LWW4HWQS/F38QW6SLWW4HWQS.jpg?auto=webp&frame=1&width=1024&height=1024&fit=bounds&md=MjAyNC0wNi0wMSAwNzowODo1Mi4w)

[![Assembling the Base](https://content.instructables.com/FIY/4S6E/LWW4HWTG/FIY4S6ELWW4HWTG.jpg?auto=webp&frame=1&width=400&height=1024&fit=bounds&md=MjAyNC0wNi0wMSAwNzoxMzoyMC4w)](https://content.instructables.com/FIY/4S6E/LWW4HWTG/FIY4S6ELWW4HWTG.jpg?auto=webp&frame=1&width=1024&height=1024&fit=bounds&md=MjAyNC0wNi0wMSAwNzoxMzoyMC4w)

[![Assembling the Base](https://content.instructables.com/FM0/FW9E/LWW4HWZJ/FM0FW9ELWW4HWZJ.jpg?auto=webp&frame=1&width=400&height=1024&fit=bounds&md=MjAyNC0wNi0wMSAwNzoxOTo1Ni4w)](https://content.instructables.com/FM0/FW9E/LWW4HWZJ/FM0FW9ELWW4HWZJ.jpg?auto=webp&frame=1&width=1024&height=1024&fit=bounds&md=MjAyNC0wNi0wMSAwNzoxOTo1Ni4w)

**Step 1 (Yellow arrows):** Slide the HuskyLens into the HuskyLens unit part. Make sure that the flat cable from the newly added camera slides between the 3D-printed parts (purple circle). The flat cable from the HuskyLens camera itself can be fitted into the space in front of the camera (orange circle). To ensure the camera stays in position, it's recommended to put some double-sided tape on the back of the camera and stick it to the 3D-printed part.

**Step 2:** We need to adjust the focus on the camera. Place the unit loosely on the base, connect the red wire from the HuskyLens to the VIN pin on the ESP32 and the black wire to a GND pin like before. Now, adjust the focus so the HuskyLens can recognize an AprilTag close enough to the camera. (Make sure the HuskyLens is set to tag recognition.)

**Step 3:** Before securing the HuskyLens unit in place, we need to thread a piece of fabric through the hole in the center of the base. This fabric will absorb the bait and attract the hornets to it.

**step 4 (Black and green arrow(s)):** Place the entire HuskyLens unit onto the base part and secure it with screws from underneath. Slide the cover part onto the base part to enclose the open side of the HuskyLens. You can secure the cover part with a rubber band if it's to loose.

**Step 5 (Blue arrow):** slide the plexiglass (acrylic) in place.

**step 6 and 7 (Red and purple arrow(s)):** There is an option to place an LED into the detection part to provide additional light if there isn’t enough for the camera to detect the AprilTags or insects. Simply slide the detection part onto the base as shown.

**Step 8 (Orange arrows):** Secure the thread part with the thread to the base using 4 screws/bolts.

## Step 6: Assembling the Roof Part

[![Assembling the Roof Part](https://content.instructables.com/FCZ/LJ41/LWW4HY64/FCZLJ41LWW4HY64.jpg?auto=webp&frame=1&width=600&height=1024&fit=bounds&md=MjAyNC0wNi0wMSAwNzo1NjozNC4w)](https://content.instructables.com/FCZ/LJ41/LWW4HY64/FCZLJ41LWW4HY64.jpg?auto=webp&frame=1&width=1024&height=1024&fit=bounds&md=MjAyNC0wNi0wMSAwNzo1NjozNC4w)

[![Assembling the Roof Part](https://content.instructables.com/F4H/6OEP/LX4P54X6/F4H6OEPLX4P54X6.jpg?auto=webp&frame=1&width=600&height=1024&fit=bounds&md=MjAyNC0wNi0wNyAwOToxNToyNC4w)](https://content.instructables.com/F4H/6OEP/LX4P54X6/F4H6OEPLX4P54X6.jpg?auto=webp&frame=1&width=1024&height=1024&fit=bounds&md=MjAyNC0wNi0wNyAwOToxNToyNC4w)

**Step 1 (Red arrows):** Thread the wires from the HuskyLens through the hole (blue circle) and secure them with a zip tie to the pillar. Then, connect the blue wire to pin 22, the green wire to pin 21, the black wire to a GND pin, and the red wire to the VIN pin. If you have an LED installed, wire the negative (shorter leg) to a GND and the positive (longer leg) to pin 4 with a 220-180 ohm resistor. Finally, slide the ESP32 into the designated slot.

**step 2 (Blue arrows):** Simply slide the entire piece into place onto the base part.

**Note:** If the middle part is sliding freely, put a piece of filament (1.75mm, +-20mm long) in the holes (yellow circles) to lock the two parts in place.

## Step 7: Assembling the Roof

[![Assembling the Roof](https://content.instructables.com/FII/2A7V/LWW4HYLJ/FII2A7VLWW4HYLJ.jpg?auto=webp&frame=1&width=1002&height=1024&fit=bounds&md=MjAyNC0wNi0wMSAwODowNToxNi4w)](https://content.instructables.com/FII/2A7V/LWW4HYLJ/FII2A7VLWW4HYLJ.jpg?auto=webp&frame=1&width=1024&height=1024&fit=bounds&md=MjAyNC0wNi0wMSAwODowNToxNi4w)

This is the easiest part of all, just slide the roof into place as shown in the picture.

## Step 8: Getting Started: Accessing the Webserver

[![Getting Started: Accessing the Webserver](https://content.instructables.com/FJC/52AG/LXRK6OMR/FJC52AGLXRK6OMR.png?auto=webp&frame=1&width=607&fit=bounds&md=MjAyNC0wNi0yMyAwNjo1OToyNy4w)](https://content.instructables.com/FJC/52AG/LXRK6OMR/FJC52AGLXRK6OMR.png?auto=webp&frame=1&fit=bounds&md=MjAyNC0wNi0yMyAwNjo1OToyNy4w)

  

### Accessing the webserver

After the assembly is completed and the code and SPIFFS are installed on the ESP32, we can access the web server by connecting to the access point created by the ESP32 once it is powered on. Go to the settings on your device and search for the WiFi network named "hornets." Connect to this WiFi network (no password needed) and open a browser. Enter the default IP address of the ESP32, "192.168.4.1"

You should see a WiFi manager page where you can enter your SSID and password for your home network. After submitting, the ESP32 will reboot and attempt to connect to the provided network. If it successfully connects, a new IP address should be visible on the HuskyLens screen. Reconnect your device to your own WiFi network and enter the new IP address in your browser. You should now see the web server.

### Changing the algorithm

It's possible to change the algorithm of the HuskyLens from the web server by pressing the "Object" or "Tags" buttons. By default, it is set to "Tags." When you press one of the buttons, the active algorithm will be displayed underneath the buttons. The "Object" algorithm is used to detect insects, while the "Tags" algorithm is used to detect AprilTags.

### controlling the LED

The LED can be controlled with the two buttons, "ON" and "OFF." The state of the LED, whether it's on or off, will be displayed.

### Adding the coordinates and area

Enter the coordinates where the trap will be placed and select the area you are in. You can easily find the coordinates using Google Maps and copy-paste them. After entering the coordinates and selecting the area, click on "Save" to save the information. Make sure that when entering the coordinates, there isn't any space between the comma and the next number:

GOOD: 51.068356,4.498862

~~BAD: 51.068356, 4.498862~~

## Step 9: You're Done

[![You're Done](https://content.instructables.com/F7R/8HJH/LXX9YGYK/F7R8HJHLXX9YGYK.jpg?auto=webp&frame=1&fit=bounds&md=MjAyNC0wNi0yNyAxMzowNDoyOS4w)](https://content.instructables.com/F7R/8HJH/LXX9YGYK/F7R8HJHLXX9YGYK.jpg?auto=webp&frame=1&fit=bounds&md=MjAyNC0wNi0yNyAxMzowNDoyOS4w)

After many hours of development and testing, we have finally completed our AI/IoT device to locate nests of the invasive Asian hornet. One aspect of this project is the ability to deploy multiple devices, enabling us to determine the nest locations even more accurately. We are proud of what we have achieved and are excited about the potential of this device to contribute to the protection of our local ecosystems.

Open Menu

AI/IoT Yellow Legged Asian Hornet Nest Localizer by [PrintThatBoii](https://www.instructables.com/member/PrintThatBoii%20/) FollowSave PDF Favorite [I Made It](https://www.instructables.com/AIIoT-Yellow-Legged-Asian-Hornet-Nest-Localizer/#ible-footer-portal) [View Comments](https://www.instructables.com/AIIoT-Yellow-Legged-Asian-Hornet-Nest-Localizer/#ible-footer-portal) Share More Options

Categories

- [
    
    Circuits](https://www.instructables.com/circuits/)
- [
    
    Workshop](https://www.instructables.com/workshop/)
- [
    
    Design](https://www.instructables.com/design/)
- [
    
    Craft](https://www.instructables.com/craft/)
- [
    
    Cooking](https://www.instructables.com/cooking/)
- [
    
    Living](https://www.instructables.com/living/)
- [
    
    Outside](https://www.instructables.com/outside/)
- [
    
    Teachers](https://www.instructables.com/teachers/)

About Us

- [Who We Are](https://www.instructables.com/about/)
- [Why Publish?](https://www.instructables.com/create/)

Resources

- [Get Started](https://www.instructables.com/Get-Started/)
- [Help](https://www.instructables.com/help/)
- [Sitemap](https://www.instructables.com/sitemap/)

Find Us

- [](https://www.instagram.com/instructables/ "Instagram")
- [](https://www.tiktok.com/@instructables "TikTok")

---

© 2025 Autodesk, Inc.

- [Terms of Service](https://www.autodesk.com/company/legal-notices-trademarks/terms-of-service-autodesk360-web-services/instructables-terms-of-service-june-5-2013)|
- [Privacy Statement](https://www.autodesk.com/company/legal-notices-trademarks/privacy-statement)|
- Privacy settings|
- [Legal Notices & Trademarks](https://www.autodesk.com/company/legal-notices-trademarks)

[![Autodesk](https://www.instructables.com/assets/img/footer/autodesk-logo-primary-white.png)](https://www.autodesk.com/)