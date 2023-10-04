"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
const fs = __importStar(require("fs"));
const csvparse = __importStar(require("csv-parse"));
// import {JSON} from "JSON";
const dns = __importStar(require("dns"));
const SUBDOMAIN = process.argv[2];
const DOMAIN = process.argv[3];
const HARFILE = process.argv[4];
// Outfilename
const OUTFILE = process.argv[5];
console.log(DOMAIN);
console.log(HARFILE);
let records = [];
let harFile = fs.readFileSync(HARFILE);
let harJson = JSON.parse(harFile.toString());
let storer = [];
// pushes the Leak onto the aStorer list
// 
function findLeak(aHar, aStr, aStorer) {
    let entryNum = 0;
    aHar.log.entries.forEach((entry) => {
        let result;
        result = {
            str: aStr,
            url: "",
            GET: "",
            POST: "",
            referer: "",
            cookie: "",
            cNames: []
        };
        result["url"] = entry.request.url;
        if (entry.request.method === "GET") {
            if (entry.request.url.match(aStr.replace('+', '\\+'))) {
                result["GET"] = entry.request.url;
            }
        }
        if (entry.request.method === "POST") {
            if (typeof (entry.request.postData) !== "undefined") {
                if (typeof (entry.request.postData.text) !== "undefined") {
                    if (entry.request.postData.text.match(aStr.replace('+', '\\+'))) {
                        result["POST"] = entry.request.postData.text;
                    }
                }
            }
        }
        for (let aHeader of entry.request.headers) {
            if (aHeader.name === "referer") {
                if (aHeader.value.match(aStr.replace('+', '\\+'))) {
                    result.referer = result.referer.concat("!".concat(aHeader.value.toString()));
                    // result.referer += "4d990200ce2148897a885be57b3c8e00e0d75f68659be3a849b9a65b";
                    // entry.request.url.includes(DOMAIN) ? 1==1 :console.log(`found in referer: ${aStr}`);
                }
            }
        }
        // console.log(result);
        for (let cookie of entry.request.cookies) {
            if (cookie.name.match(aStr.replace('+', '\\+')) || cookie.value.match(aStr.replace('+', '\\+'))) {
                result["cookie"] = result.cookie.concat("!".concat(cookie.name.concat(cookie.value)));
                // entry.request.url.includes(DOMAIN) ? 1==1 : console.log(`found in cookie: ${aStr}`); 
            }
        }
        // result.referer !== "" ? console.log(result) : 1==1 ; 
        if (result.GET !== "" || result.POST !== "" || result.cookie !== "" || result.referer !== "") {
            aStorer.push(result);
        }
        entryNum++;
    });
}
//records: a 2d that represents the csv of the hashes to look for
//
function processRecords(records, harJson, aStorer) {
    for (let i = 1; i < 27; i = i + 1) {
        for (let j = 0; j < 55; j++) {
            findLeak(harJson, records[i][j].toString(), aStorer);
        }
    }
}
function printAll(aStorer, outFile) {
    for (let aLeak of aStorer) {
        fs.appendFileSync(outFile, JSON.stringify(aLeak, null, 2) + ", ");
        fs.appendFileSync(outFile, "\n");
    }
}
function piiMethod(aLeak) {
    if (aLeak.GET !== "") {
        return "get";
    }
    else if (aLeak.POST !== "") {
        return "post";
    }
    else if (aLeak.cookie !== "") {
        return "cookie";
    }
    else if (aLeak.referer !== "") {
        return "referer";
    }
}
//takes the hashes file, 
// takes the har file
fs.createReadStream("./final_hashes_for_lookup.csv")
    .pipe(csvparse.parse())
    .on("data", (data) => {
    records.push(data);
    // console.log(data);
})
    .on("end", () => {
    console.log("domain: " + DOMAIN);
    console.log("harfile: " + HARFILE);
    console.log("outfile: " + OUTFILE);
    processRecords(records, harJson, storer);
    // get rid of repeats
    // storer = storer.filter((item, index, arr) => arr.indexOf(item) === index);
    storer = storer.filter((aLeak) => {
        // only those that go back to the same eTLD, but not same eTLD+1, same site but not same origin
        return aLeak["url"].includes(DOMAIN.slice(0, DOMAIN.length - 1)) && (!aLeak["url"].includes(SUBDOMAIN.concat(DOMAIN.slice(0, DOMAIN.length - 1))));
    }).map((aLeak) => {
        aLeak["cNames"].push((new URL(aLeak.url).hostname));
        return aLeak;
    });

    let f = (aLeak) => ((err, ipAddresses) => {
        if (err) {
            // there is no cname
            console.log(err);
            return;
        }
        else {
            // there is a cname
            aLeak["cNames"].push(ipAddresses[0]);
            return dns.resolveCname(aLeak["cNames"][aLeak["cNames"].length - 1], f(aLeak));
        }
    });

    storer.forEach((aLeak) => {
        dns.resolveCname(aLeak["cNames"][aLeak["cNames"].length - 1], f(aLeak));
    });
    storer = storer
    // check if at least one cname is different site
    .filter((aLeak) => {
        return aLeak["cNames"].reduce((acc, currentVal) => {
            return acc || (!currentVal.includes(DOMAIN.slice(0, DOMAIN.length - 1)));
        }, false);
    })
    // if the leaks were useless do not print
    // .filter((aLeak) => {
    //     return aLeak["str"] !== "60201" && aLeak["str"] !== "Evanston" && aLeak["str"] !== "Illinois";
    // })
    // remove duplicates
    .filter((item, index, arr) => {
        // remove duplicates
        return arr.indexOf(item) === index;
    });
    printAll(storer, OUTFILE.concat(".json"));
    console.log(OUTFILE.concat(".json"));
    // Promise.all(storer.map((aLeak : Leak) => 
    //     {
    //         return dns.promises.resolveAny((new URL(aLeak.url).hostname))
    //     })).then((results) => {
    //         if (results.length !== storer.length){
    //             console.log("NOT SAME LENGTH"); 
    //             process.exit(); 
    //         }
    //         else{
    //             console.log("SAME LENGTH"); 
    //         }
    //         // we want to follow the cname chains 
    //         let leaksWithCnames = results.map((aResult,index)=> {
    //             return {"result1":aResult, "leak": storer[index]}
    //             // here we get those leaks that are paired with cnames 
    //         }).filter( (aStruct) => {
    //             return aStruct["result1"].reduce((acc, currentVal) => {return acc || currentVal["type"] === "CNAME"}, false)
    //             // keep cnames drop the rest
    //         });
    //         Promise.all(leaksWithCnames.map((aLeakAndCname) => 
    //         {
    //             if (aLeakAndCname["result1"].length !== 1){
    //                 console.log(aLeakAndCname["result1"])
    //                 console.log("more than 1"); 
    //                 process.exit(); 
    //             }
    //             return dns.promises.resolveAny( (aLeakAndCname["result1"][0] as dns.AnyCnameRecord)["value"])
    //         })).then((results) =>{
    //             let leaksWithCnames2 = results.map((item,index)=> {
    //                 return {
    //                     "result2": item.filter((resultRound2)=>{return resultRound2["type"] === "CNAME"}, false),
    //                     "result1": leaksWithCnames[index]["result1"],
    //                     "leak": leaksWithCnames[index]["leak"]
    //                 }
    //                 // here we get those leaks that are paired with cnames 
    //             });
    //             leaksWithCnames2.forEach((anItem) => {
    //                 if (anItem["result2"].length > 0){
    //                     console.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    //                     console.log(anItem);
    //                 }
    //             });
    //             let round3 = leaksWithCnames2.reduce((acc, currentVal)=>{return acc || (currentVal["result2"].length > 0)}, false);
    //             if (round3){
    //                 console.log("needs round 3!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"); 
    //             }
    //             else {
    //                 leaksWithCnames2 = leaksWithCnames2.filter((x)=>{
    //                     return !((x["result1"][0] as dns.AnyCnameRecord)["value"].includes(DOMAIN.slice(0,DOMAIN.length -1)))
    //                 });
    //                 printAll(leaksWithCnames2, OUTFILE.concat(".json")); 
    //                 console.log(OUTFILE.concat(".json"));
    //             }
    //         }).catch((err) =>{
    //             console.error(err);
    //         });                 
    //     })
    //     .catch((err) => {
    //         console.error(err);
    //     });
    // let theCnames :dns.AnyRecord[][]  = results.map((aResult : dns.AnyRecord[]) => {
    //     return aResult.filter((aRecord ) => { return aRecord["type"] === "CNAME"} ) 
    // })
    // leaksWithCnames.forEach((item) => {
    //     console.log(item["result"]);
    //     console.log(item["leak"]);
    // });
    // printAll(leaksWithCnames, OUTFILE.concat(".json")); 
    // console.log(OUTFILE.concat(".json"));
    // printAll(storer
    //     .filter((aLeak)=>{return (aLeak.url.includes(DOMAIN))})
    //     .filter((item, index, arr) => arr.indexOf(item) === index),
    //      OUTFILE.concat("_first_party.json")); 
    // const ipAddresses = results.flat();
    // printAll(storer
    //     .filter((aLeak)=>{return (aLeak.url.includes(DOMAIN))})
    //     .filter((item, index, arr) => arr.indexOf(item) === index),
    //      OUTFILE.concat("_third_party.json")); 
    // printAll(storer
    //     .filter((aLeak)=>{return !(aLeak.url.includes(DOMAIN))})
    //     .filter((item, index, arr) => arr.indexOf(item) === index),
    //      OUTFILE.concat("_third_party.json")); 
    // printAll(storer
    //     .filter((aLeak)=>{return !(aLeak.url.includes(DOMAIN))})
    //     .filter((item, index, arr) => arr.indexOf(item) === index),
    //      OUTFILE.concat("_third_party.json")); 
    // console.log(OUTFILE.concat("_third_party.json"));
    // printAll(storer.filter((aLeak)=>{return !(aLeak.url.includes(DOMAIN))})
    //     .map((aLeak) => { return {"leakedString" : aLeak.str, "url" : aLeak.url}; })
    //     .filter((item, index, arr) => arr.indexOf(item) === index)
    //     , OUTFILE.concat("_strings_urls.json") );
    // console.log(OUTFILE.concat("_strings_urls.json"));
    // printAll(storer.filter((aLeak)=>{return !(aLeak.url.includes(DOMAIN))})
    //     .map((aLeak) => { return `${DOMAIN}, general news, yes, yes, ${aLeak.str}, hashing, ${piiMethod(aLeak)}, ${(new URL(aLeak.url)).hostname}, requires_authentication` })
    //     .filter((item, index, arr) => arr.indexOf(item) === index) 
    //     , 
    //     OUTFILE.concat(".csv"));
    // console.log(storer)
});
