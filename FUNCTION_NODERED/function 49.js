var folders=context.global.get("folders") || []

if (msg.payload==='DELETE'){
    console.log("FOLDERS DA: ",folders)

    msg.payload=folders.map(folders=>`rm -r '${folders}'`).join(' && ');
    console.log("FOLDERE DE STERS",msg.payload)
    folders=folders.filter(folders=>folders.length>0);
    console.log("FOLDERE GLOBALIST:",folders)
    context.global.set('folders',[])
    console.log("FOLDERE GLOBALIST 2:",folders)
}else{
    msg.payload="echo 'No folders to delete'";
    console.log("CEVA",msg.payload)
}
return msg;