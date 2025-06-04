import React from 'react';
import "bootstrap/dist/css/bootstrap.min.css";


function ErrorToast(){

return(
    
    <div id="snackbar">
        <img src="./img/error-icon.png" id="snackbar-icon" width="90" height="40"/> 
        <span id="snackbar-title" ></span>
       </div>    
);
}
    
export default ErrorToast;