//UI management
async function runApp(){
  const menuButton = document.getElementById('menuButton');
  const menuHeader = document.getElementById('menuHeader');
  const userName = menuHeader.getAttribute('context-username');
  window.init = initMap();
  let currentStep;
  async function getUserStatus(){
    response = await fetch("/map/get-user-status/")
    const responseData = await response.json();
    const active = responseData.active_rental
    if (active){
        currentStep = 'end';
    }else{
        currentStep = 'scan';
    }
  }
  await getUserStatus();

  async function updateUI(){
    if (currentStep === 'scan') {
      menuButton.textContent = 'Scan';
      menuHeader.textContent = `Hello, ${userName}`;
      menuButton.onclick = () => window.location.href = "/map/scanner/";
    } else if (currentStep === 'start') {
      menuButton.textContent = 'Start Ride';
      const bike_code = await GetBikeCode(sessionStorage.getItem('bike_id'),"/map/get-bike-code/");
      menuHeader.textContent = `Your code is: ${bike_code}`;
      menuButton.onclick = async () => {
    const response = await fetch("/map/start-rental/", {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },body: JSON.stringify({'bike_id':sessionStorage.getItem('bike_id')})});
      currentStep = 'end';
      sessionStorage.removeItem('bike_id');
      updateUI();};
    } else if (currentStep === 'end') {
      menuButton.textContent = 'End Ride';
      menuHeader.textContent = 'Enjoy your trip!';
      menuButton.onclick = async () => {
        response = await endRide("/map/end-rental/");
        if (response.status ==200){
          currentStep = 'scan';
          updateUI();
        }else if (response.status ==400){
          currentStep="end"
          menuHeader.textContent="You can't park here"
          console.log(menuHeader.textContent)   
        }
      };
   }
  };

  if (sessionStorage.getItem('bike_id')) {
    currentStep = 'start';
  }
  updateUI();
}


//API management
async function GetBikeCode(bike_id,link) {
    const url = new URL(link, base=window.location.origin);
    url.search = new URLSearchParams({ "bike_id": bike_id });
    const response = await fetch(url);
    const data = await response.json();
    return data.bike_code
  
}

async function GetBikes(){
  const response = await fetch("/map/get-bike-positions/");
  const responseData = await response.json();
  return responseData.bikes
}

async function GetPolygons(){
  const response = await fetch("/map/get-polygons/");
  const responseData = await response.json();
  return responseData.polygons
}

async function AddMarker(bike){
  const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
  const marker = new AdvancedMarkerElement({
    map,
    position: { lat: bike.lat, lng: bike.lon },
  });     
  markers.push(
    {
      bike_id: bike.id,
      "marker" : marker,
    });
}

async function SetMarkers(){
  //Current bike list
  const bikes = await GetBikes();
  const getBikesIdList = () =>{
    let bikes_id = [];
    for (let bike of bikes){
      bikes_id.push(bike.id);
    }
    return bikes_id;
  };
  const getMarkersIdList = () =>{
    let ids = [];
    for (let marker of markers){
      ids.push(marker.bike_id);
    }
    return ids;
  };
  const bikesIds = new Set(getBikesIdList());
  const markerIds = new Set(getMarkersIdList());

  for (let bike of bikes){
    if (markerIds.has(bike.id)){
      continue; // All good the bike is displayed
    } else{
      await AddMarker(bike);
    }
  }

  for (let i = markers.length - 1; i >= 0; i--) {
    const marker = markers[i];
    if (bikesIds.has(marker.bike_id)) {
        continue
    } else {
      //Delete marker
      marker.marker.setMap(null);
      //Using splice we can adjust the size of array to the current number of bikes
      markers.splice(i, 1);
    }
  }
}
async function SetPolygons(){
  const polygons = await GetPolygons()
  for (let poly of polygons){
    const polygon = new google.maps.Polygon({
    paths: poly.coords,
    strokeColor: "#2ad438",
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: "#2ad438",
    fillOpacity: 0.35
    });
    polygon.setMap(map);
  }
}
function getLocation() {
  return new Promise((resolve, reject) => {
      if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(
              (position) => {
                  const location = {
                      "lat": position.coords.latitude,
                      "lon": position.coords.longitude
                  };
                  resolve(location);
              },
              (error) => reject(error)
          );
      } else {
          reject("Geolocation is not supported by this browser.");
      }
  });
}

async function endRide(link) {
  let location;
  try {
    location = await getLocation();
    console.log("Location:", location);
  } catch (error) {
    console.error("Error getting location:", error);
  }

  url = new URL(link, window.location.origin)
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(location)});
    return response
}

(g=>{var h,a,k,p="The Google Maps JavaScript API",c="google",l="importLibrary",q="__ib__",m=document,b=window;b=b[c]||(b[c]={});var d=b.maps||(b.maps={}),r=new Set,e=new URLSearchParams,u=()=>h||(h=new Promise(async(f,n)=>{await (a=m.createElement("script"));e.set("libraries",[...r]+"");for(k in g)e.set(k.replace(/[A-Z]/g,t=>"_"+t[0].toLowerCase()),g[k]);e.set("callback",c+".maps."+q);a.src=`https://maps.${c}apis.com/maps/api/js?`+e;d[q]=f;a.onerror=()=>h=n(Error(p+" could not load."));a.nonce=m.querySelector("script[nonce]")?.nonce||"";m.head.append(a)}));d[l]?console.warn(p+" only loads once. Ignoring:",g):d[l]=(f,...n)=>r.add(f)&&u().then(()=>d[l](f,...n))})({
    key: "AIzaSyDqaEmMUlCcnwrTtVb0e467mhQryaPAJTI",
    v: "weekly",
    // Use the 'v' parameter to indicate the version to use (weekly, beta, alpha, etc.).
    // Add other bootstrap parameters as needed, using camel case.
  });
  let map;
  const markers = []

  async function initMap() {
  const { Map } = await google.maps.importLibrary("maps");
  //const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

  map = new Map(document.getElementById("map"), {
      center: { lat: 50.063481, lng: 19.932906 },
      zoom: 16,
      disableDefaultUI: true,
      mapId: 'f203d7d130752d37'
    });

  await SetPolygons();
  await SetMarkers();
  setInterval(SetMarkers, 10000);
}