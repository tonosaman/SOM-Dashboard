# SOM Dashboard
2021.2 has Bokeh and dashboard installed, and does not require installation. The Bokeh server is also started automatically, URL is printed out before login.

To start Bokeh server manually, use one of the following commands:

    sudo /etc/init.d/som-dashboard start

or

    sudo bokeh serve --show --allow-websocket-origin=*IP_ADDRESS*:5006 /usr/lib/python3.8/site-packages/som-dashboard
    

in a browser go to the following url:

    
    http://*IP_ADDRESS*:5006/som-dashboard
    

    

Current view:
![Alt text](snapshot1.PNG?raw=true "Title")
![Alt text](snapshot2.PNG?raw=true "Title")

# License
Licensed under the Apache License, Version 2.0 (the “License”); you may not use this file except in compliance with the License.

You may obtain a copy of the License at apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an “AS IS” BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the Licens
