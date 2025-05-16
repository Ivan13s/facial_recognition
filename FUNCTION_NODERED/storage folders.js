// storage folders
var folders=context.global.get("folders") || [] //folderele salvate global
console.log("PRIMUL",folders)
var newFolder=msg.payload //folder curent primit 
folders.push(newFolder)
context.global.set("folders",folders);
///folders=folders.filter((item,index,self)=>self.findIndex(f=>f.path===item.path)===index);
console.log("FOLDER 2",folders)
var counts=folders.reduce((acc,path)=>{
    acc[path] = (acc[path] || 0)+1;
    return acc;
},{});
var duplicates=Object.keys(counts).filter(path=>counts[path]>1);
console.log("Duplicate folders: ",duplicates)

folders=folders.filter(folderArray=>!duplicates.includes(folderArray[0]));
context.global.set("folders",folders)
console.log("Folders fara duplicate ",folders)
return null // nu trimite mai departe doar salveaza
