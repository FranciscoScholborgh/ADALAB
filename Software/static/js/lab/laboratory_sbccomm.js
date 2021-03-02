function webSocketSBC(canvas_id, device, time, execute, onSuccess, onFail){
    var gateway = `wss://djangowstest.herokuapp.com/ws/device/${device}/`;
    var timeout = 10; 
    var recived = 0;
    var websocket = new WebSocket(gateway);
    websocket.onopen    = onOpen;
    websocket.onclose   = onClose;
    websocket.onmessage = onMessage;

    function timer() { 
        timeout = timeout - 1;
        //console.log(timeout + ' seconds left');
        if (timeout >= 1 && recived < time){
            setTimeout(timer, 1000);
        } else if (recived < time) {
            var title = "Error de conexion";
            var content = `No se logro establecer conexión con el dispositivo ${device} de forma estable, por favor verifique su internet y el dispositivo `;
            if(canvas_id === undefined){
                onFail(title, content);
            } else {
                onFail(canvas_id, title, content);
            }
            websocket.close();
        }
    }  
    
    function onOpen(event) {
        //console.log(`Connection ${device} opened`);
        setTimeout(timer, 1000);
    }

    function onClose(event) {
        //console.log(`Connection ${device} closed`);
    }

    function onMessage(event) {
        recived = recived + 1;
        if( event === `${device}-OFFLINE`) {
            var title = "Error de conexion";
            var content = `No se logro establecer conexión con el dispositivo ${device} de forma estable, por favor verifique su internet y el dispositivo `;
            if(canvas_id === undefined){
                onFail(title, content);
            } else {
                onFail(canvas_id, title, content);
            }
        } else {
            if(timeout < 10){
                timeout++;
            }
            var jsonData = JSON.parse(event.data);
            if (canvas_id === undefined) {
                execute(jsonData);
            } else {
                execute(canvas_id, jsonData);
            }
        }
        
        if(recived >= time) {
            if (canvas_id === undefined) {
                onSuccess();
            } else {
                onSuccess(canvas_id);
            }               
            websocket.close();
        }
    }
}
