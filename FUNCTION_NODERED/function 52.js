//function 52
const fs = global.get('fs');
const filePath="/home/ivan/opencv/build/facial_recognition_var2/log_persoane_cunoscute.txt";
let currentLineIndex=0;
function processNewLines(){
    fs.readFile(filePath,"utf8",(err,data)=>{
        if(err){
            console.error("Eroare",err);
            return null
        }
        const lines=data.split("\n").map(line=>line.trim()).filter(line=>line.length>0);
        while (currentLineIndex<lines.length){
            let msg={
                topic:"new_line",
                payload:lines[currentLineIndex]
            }
            node.send(msg);
            currentLineIndex++;
        }
    })
}

fs.watch(filePath,(eventType)=>{
    if(eventType==="change"){
        processNewLines();
    }
});
processNewLines()