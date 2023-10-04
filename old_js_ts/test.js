const myURL = new URL('https://www.example.org/foo');
console.log(myURL.href);
console.log(myURL.host);
console.log(myURL.hostname);


// Prints https://example.org/foo

myURL.href = 'https://example.com/bar';
console.log(myURL.href);