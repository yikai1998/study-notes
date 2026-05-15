function formatNumberWithTwoDecimals(number) {
  var number = Number(number)

  var options = {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  };
  var formattedNumber = number.toLocaleString('en-US', options);

  return formattedNumber
  // Logger.log(formattedNumber); // Output will be '1,234,567.89'
}
