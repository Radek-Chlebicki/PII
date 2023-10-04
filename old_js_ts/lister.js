const fs = require('fs');
const path = require('path');

const dirPath = './general_news_cnames'; // replace with the actual path to your directory

fs.readdir(dirPath, (err, files) => {
  if (err) {
    console.error(err);
    return;
  }

  files.forEach((filename) => {
    const filePath = path.join(dirPath, filename);
    if (fs.statSync(filePath).isFile()) {
      const fileContent = fs.readFileSync(filePath, 'utf-8');
      const updatedContent = `[${fileContent.slice(0, -1)}]`;
      fs.writeFileSync(filePath, updatedContent);
    }
  });
});
