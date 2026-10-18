import {chromium} from '/opt/node22/lib/node_modules/playwright/index.mjs';
const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:1400,height:1400}});
for(const [name,qs] of JSON.parse(process.argv[2])){
  await p.goto('http://localhost:8765/index.html?'+qs);await p.waitForFunction(()=>document.title==='done',null,{timeout:120000});
  await p.screenshot({path:name});console.log(name);}
await b.close();
