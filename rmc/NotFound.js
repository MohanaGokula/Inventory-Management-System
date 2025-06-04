  import React from 'react';
  import Sidebar from './Sidebar';
  function NotFound() 
  {
    return(
        <>
            <div id="outer-container"  className="App"  > 
            <Sidebar pageWrapId={'page-wrap'} outerContainerId={'outer-container'} />
                <div id="page-wrap">
                        <div id="header">
                            <h2 className = "text font-weight-bold page-title">Not Found</h2>
                            <h4 style={{textAlign:"center"}}>The requested URL was not found on this server.</h4>
                        </div>
                </div><br/>
            </div> 
        </>
    );
  }
  export default NotFound;
