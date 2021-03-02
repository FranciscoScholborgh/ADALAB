var CACHE_NAME = 'adaslabpwacache-v1.0';

var urlsToCache = [
    '/login/',
    '/register/',
    '/reset_password/',
    '/',
    '/ADASLAB/',
];

self.addEventListener('install', function(event) {
    // Perform install steps
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            //console.log('Opened cache');
            return cache.addAll(urlsToCache);
        })
    );
});

self.addEventListener('fetch', function(event) {

    if ( event.request.url.indexOf('/preinforme/') !== -1 ) {    
        return event;
    } else {
        event.respondWith(
            fetch(event.request).then((result)=>{
                return caches.open(CACHE_NAME)
                .then(function(c) {
                c.put(event.request.url, result.clone())
                return result;
                })
            })
            .catch(function(e){
                return caches.match(event.request)
            })
        );
    }    
});
