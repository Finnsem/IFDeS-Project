// truecaller_service.js
const truecallerjs = require("truecallerjs");

const performTruecallerSearch = async (number, countryCode, installationId) => {
  const searchData = {
    number: number,
    countryCode: countryCode,
    installationId: installationId,
  };

  try {
    const response = await truecallerjs.search(searchData);
    console.log(JSON.stringify(response.json()));
  } catch (error) {
    console.error("Error occurred:", error);
  }
};

// Read arguments from command line
const args = process.argv.slice(2);
const [number, countryCode, installationId] = args;

performTruecallerSearch(number, countryCode, installationId);
