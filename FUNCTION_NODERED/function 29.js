//Aceasta functie se leaga la nodul switch,configuratiia fiind:
//cele 3 butoane(START SERVER,START TRAIN MODEL,STOP)->switch->function 29->tcp request

if (msg.payload==="b"){
    global.set('serverStatus',true);
    msg.payload='b';
    return msg;
}else if (msg.payload=== "q"){
    global.set('serverStatus',false)
    msg.payload="q";
    return msg;
}else if (msg.payload==="t"){
    if (global.get('serverStatus')===true){
        return msg;
    }else{
        msg.payload="Serverul nu este pornit";
        node.error("Serverul nu este pornit",msg)
        return null;
    }
}