import React from 'react';
import { elastic as Menu } from 'react-burger-menu';
import { Menu as AntdMenu } from 'antd';
import './Sidebar.css';
import 'bootstrap/dist/css/bootstrap.css';
import Dropdown from 'react-bootstrap/Dropdown';
import {ButtonGroup} from 'react-bootstrap';
import { useNavigate } from 'react-router';
import { useCookies } from 'react-cookie';
import { useState ,useEffect } from "react";
import {Button} from "reactstrap";



export default props => {
  let navigate = useNavigate();
  const [cookies, setCookie, removeCookie] = useCookies(['myToken']);
  const [name, setName,removeName] = useCookies(['myName']);
  const [category, setCategory,removeCategory] = useCookies(['myCategory']);
  const [superuser,setSuperuser,removeSuperuser] = useCookies(['mySuperuser']);
  // const [openKeys, setOpenKeys] = useState([]);
  
  // const handleSubMenuClick = (openKeys) => {
  //   setOpenKeys(openKeys);
  // };
  
  useEffect(() => {
    if(!cookies['myToken']){  //checks for a cookie named mytoken
		console.log(cookies['myToken']+"cookies['myToken']")
		window.location.href = '/'
	}
  }, [cookies]);
  return (
    
    <Menu>
      <AntdMenu theme="dark" mode="inline" style={{ width: 250,backgroundColor:"rgb(2, 2, 49)",fontWeight:"bold" }} >
      
         <AntdMenu.SubMenu key="purchase" title='PURCHASE'>
           
               <AntdMenu.Item key="purchase_order" onClick={() =>{navigate("/PurchaseOrder")}}>
                Purchase Order
                </AntdMenu.Item>
            
          </AntdMenu.SubMenu>
       

        
        
      </AntdMenu>
    </Menu>
  );
  };   
       
        
