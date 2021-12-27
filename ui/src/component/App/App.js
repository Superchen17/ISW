import React from 'react';
import {Menu, Layout} from 'antd';

import 'antd/dist/antd.css';

import PageIR from '../page-ir';
import PageISW from '../page-isw';
import { Hidden } from '@material-ui/core';

class App extends React.Component{
    constructor(props){
        super(props);

        this.state = {
            topic: 'ir', //* {'ir', 'isw'}
        }
    }

    change_epic = (e) => {
        this.setState({
            topic: e.key
        })
    }

    render(){
        return (
            <Layout style={{minHeight: '100vh'}}>
                <Layout.Header>
                    <Menu theme="dark" mode="horizontal">
                        <Menu.Item key="ir" onClick={this.change_epic}>
                            Image Registration
                        </Menu.Item>
                        <Menu.Item key="isw" onClick={this.change_epic}>
                            Water Distortion Restoration
                        </Menu.Item>
                    </Menu>
                </Layout.Header>

                {
                    this.state.topic === 'ir'
                    ? <PageIR />
                    : <PageISW />
                }
            </Layout>
        );
    }
}

export default App;
