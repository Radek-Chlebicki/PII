"use strict";
// col 1 : raw pii njaymd
// col 2: first col value which is true form such as roger
// col 3: how it was encoded : pii column header such as base64
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
function getHashRow(arow) {
    const [original, ...rest] = arow.map((elem) => { return elem.toString(); });
    const [plaintext, md5, sha224, sha256, sha1, sha512, base64, base32, md4, base16, sha384, md5ofsha224, md5ofsha256, md5ofsha1, md5ofsha512, md5ofsha384, md5ofbase64, md5ofmd4, md5ofbase32, sha256ofbase64, sha256ofmd5, sha256ofmd4, sha256ofsha1, sha256ofsha224, sha256ofsha384, sha256ofsha512, sha256ofbase32, sha256ofbase16, sha512ofbase64, sha512ofmd5, sha512ofmd4, sha512ofsha1, sha512ofsha224, sha512ofsha384, sha512ofsha256, sha512ofbase32, sha512ofbase16, sha1ofbase64, sha1ofmd5, sha1ofmd4, sha1ofsha512, sha1ofsha224, sha1ofsha384, sha1ofsha256, sha1ofbase32, sha1ofbase16, sha256ofmd5ofbase64, sha256ofmd5ofsha224, sha256ofmd5ofsha1, sha256ofsha1ofmd5, md5ofsha256ofbase64, md5ofsha1ofsha256, md5ofsha256ofsha1, md5ofsha256ofsha224] = rest;
    return {
        original,
        plaintext,
        md5,
        sha224,
        sha256,
        sha1,
        sha512,
        base64,
        base32,
        md4,
        base16,
        sha384,
        md5ofsha224,
        md5ofsha256,
        md5ofsha1,
        md5ofsha512,
        md5ofsha384,
        md5ofbase64,
        md5ofmd4,
        md5ofbase32,
        sha256ofbase64,
        sha256ofmd5,
        sha256ofmd4,
        sha256ofsha1,
        sha256ofsha224,
        sha256ofsha384,
        sha256ofsha512,
        sha256ofbase32,
        sha256ofbase16,
        sha512ofbase64,
        sha512ofmd5,
        sha512ofmd4,
        sha512ofsha1,
        sha512ofsha224,
        sha512ofsha384,
        sha512ofsha256,
        sha512ofbase32,
        sha512ofbase16,
        sha1ofbase64,
        sha1ofmd5,
        sha1ofmd4,
        sha1ofsha512,
        sha1ofsha224,
        sha1ofsha384,
        sha1ofsha256,
        sha1ofbase32,
        sha1ofbase16,
        sha256ofmd5ofbase64,
        sha256ofmd5ofsha224,
        sha256ofmd5ofsha1,
        sha256ofsha1ofmd5,
        md5ofsha256ofbase64,
        md5ofsha1ofsha256,
        md5ofsha256ofsha1,
        md5ofsha256ofsha224,
    };
}
function convertToRawMeasurementObject(anarr) {
    let obj = {
        website: anarr[0].toString(),
        category: anarr[1].toString(),
        reachable_or_not: anarr[2].toString(),
        pii_leakage_or_not: anarr[3].toString(),
        raw_PII: anarr[4].toString(),
        useless: anarr[5].toString(),
        method: anarr[6].toString(),
        third_party: anarr[7].toString(),
        requires_authentication: anarr[8].toString()
    };
    return obj;
}
function getEncodingAlgorithm(aHash, hashRowRecords) {
    for (let row in hashRowRecords) {
    }
}
function getStringEncoded(aHash) {
}
function clean(item) {
    // let aFair = 
}
let study_records = [];
let hash_row_record = [];
fs.createReadStream("./ISE_DATASET - Sheet1.csv")
    .pipe(csvparse.parse())
    .on("data", (data) => {
    study_records.push(convertToRawMeasurementObject(data));
})
    .on("end", () => {
    fs.createReadStream("./final_hashes_for_lookup.csv")
        .pipe(csvparse.parse())
        .on("data", (data) => {
        hash_row_record.push(getHashRow(data));
    })
        .on("end", () => {
        // here both the hash rows and the study records are ready 
    });
});
