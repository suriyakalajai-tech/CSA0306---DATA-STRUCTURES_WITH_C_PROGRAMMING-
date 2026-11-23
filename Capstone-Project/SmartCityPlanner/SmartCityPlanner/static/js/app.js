let mapObj=null, facilityMarkers=[], localityMarkers=[];
function initMap(id,facilities,locations,mini=false){
 const el=document.getElementById(id); if(!el)return;
 mapObj=L.map(id,{zoomControl:true}).setView([13.0827,80.2707],mini?10:11);
 L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap contributors'}).addTo(mapObj);
 facilities.forEach(f=>{let m=L.circleMarker([f.lat,f.lon],{radius:mini?4:7,color:'#2878d0',fillColor:'#4ea1f5',fillOpacity:.9,weight:1}).addTo(mapObj).bindPopup(`<b>${f.name}</b><br>${f.category}<br>${f.locality}`);});
 locations.forEach(l=>L.circleMarker([l.lat,l.lon],{radius:mini?3:5,color:'#168b70',fillColor:'#20b48b',fillOpacity:.8}).addTo(mapObj).bindPopup(`<b>${l.name}</b><br>Locality reference`));
 if(mini) setTimeout(()=>mapObj.invalidateSize(),250);
}
function initInteractiveMap(data){
 const m=L.map('cityMap').setView([13.0827,80.2707],11); mapObj=m;
 const osm=L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap contributors'});
 const dark=L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',{attribution:'© OpenStreetMap © CARTO'});
 osm.addTo(m); document.getElementById('basemap').onchange=e=>{m.eachLayer(l=>{if(l instanceof L.TileLayer)m.removeLayer(l)});(e.target.value==='dark'?dark:osm).addTo(m)};
 const fg=L.layerGroup().addTo(m), lg=L.layerGroup().addTo(m);
 function render(){
  fg.clearLayers();lg.clearLayers();
  const filter=document.getElementById('facilityFilter').value;
  data.facilities.filter(f=>filter==='All'||f.category===filter).forEach(f=>{
   const marker=L.circleMarker([f.lat,f.lon],{radius:7,color:'#176cc0',fillColor:'#4a9ef2',fillOpacity:.9}).addTo(fg);
   marker.on('click',()=>{document.getElementById('featureName').textContent=f.name;document.getElementById('featureInfo').innerHTML=`<b>Category:</b> ${f.category}<br><b>Locality:</b> ${f.locality}<br><b>Coordinates:</b> ${f.lat}, ${f.lon}`});
   marker.bindTooltip(f.name);
  });
  data.locations.forEach(l=>L.circleMarker([l.lat,l.lon],{radius:5,color:'#13836b',fillColor:'#27b18c',fillOpacity:.8}).addTo(lg).bindTooltip(l.name).on('click',()=>{document.getElementById('featureName').textContent=l.name;document.getElementById('featureInfo').textContent=`Locality reference point · ${l.lat}, ${l.lon}`}));
  if(!document.getElementById('facLayer').checked)m.removeLayer(fg);else m.addLayer(fg);
  if(!document.getElementById('locLayer').checked)m.removeLayer(lg);else m.addLayer(lg);
 }
 ['facilityFilter','facLayer','locLayer'].forEach(id=>document.getElementById(id).addEventListener('change',render));render();
}
document.addEventListener('DOMContentLoaded',()=>{const t=document.getElementById('themeToggle');if(t)t.onclick=()=>document.body.classList.toggle('dark-theme')});
