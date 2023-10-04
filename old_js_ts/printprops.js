const fs = require('fs');
const path = require('path');

const dirPath = './general_news_cnames'; // replace with the actual path to your directory
const outputPath = './summary1.csv'; // replace with the actual path to your output file

const outputStream = fs.createWriteStream(outputPath, { flags: 'a' }); // create a writable stream to the output file


fs.readdir(dirPath, (err, files) => {
  if (err) {
    console.error(err);
    return;
  }

  files.forEach((filename) => {
    const filePath = path.join(dirPath, filename);
    if (fs.statSync(filePath).isFile()) {
      const fileContent = fs.readFileSync(filePath, 'utf-8');
      const data = JSON.parse(fileContent);
      data.forEach((obj) => {
        console.log(`url: ${obj.url}, cNames: ${obj.cNames.join(', ')}`);
        outputStream.write(`${obj.url}, ${obj.cNames.join(', ')}\n`); // write the output to the file

      });
      console.log("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
      outputStream.write("\n"); // write the output to the file

    }
  });
});