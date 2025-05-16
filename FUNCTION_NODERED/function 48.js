//function48
var folders=Array.isArray(msg.payload)?
msg.payload:[msg.payload];
folders=folders.map(f=>({
    path:`/home/ivan/opencv/build/facial_recognition_var2/dataset/${f.title}`,
    isChecked:f.isChecked
}))
folders=folders.filter((item,index,arr)=>arr.findIndex(f=>f.path===item.path)===index);
console.log("FOLDER F 20 filter",folders)

msg.payload=folders.map(f=>f.path);
console.log("msg.payload: ",msg.payload)
return msg;
