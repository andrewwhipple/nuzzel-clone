import React from 'react'

import logo from './logo.svg';
import './App.css';


class LinkList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      links: []
    }

    this.getLinks = this.getLinks.bind(this);

  }

  getLinks() {
    fetch('/api/users/1/following_tweets', {
      method: 'POST'
    }).then((res) => {
      console.log("New tweets grabbed");
    }).catch(() => console.log('Error filling tree'));
    
    
    fetch('/api/user/1/following_tweets?urls_only=true&time_limit=24', {
      method: 'GET',
    }).then((res) => {
      res.json().then((responseJson) => {
        //console.log(responseJson);
        this.setState(
          {
            links: responseJson
          }
        )
      })
    }).catch(() => console.error('Error in fetching tweets'));
  }
  
  
  
  render() {
    
    let linksArray = [];
    let linksDict = {};
    for (let link in this.state.links) {

      if (this.state.links[link].url in linksDict) {
        let sharers = linksDict[this.state.links[link].url];
        if (!sharers.find((name) => name == this.state.links[link].name)) {
          sharers.push(this.state.links[link].name);
        }
        
        linksDict[this.state.links[link].url] = sharers;

      } else {
        linksDict[this.state.links[link].url] = [this.state.links[link].name];
      }
    
    }

    for (let new_link in linksDict) {
      linksArray.push(<Link key={new_link} link={new_link} sharers={linksDict[new_link]}/>);
    }

    linksArray.sort((first, second) => {
      if (first.props.sharers.length > second.props.sharers.length) {
        return -1;
      } else if (first.props.sharers.length < second.props.sharers.length) {
        return 1;
      } else {
        return 0;
      }
    })

    return (
      <div>
        {linksArray}
        <button type="button" onClick={this.getLinks}>Refresh</button>
      </div>
    )
  }
}

class Link extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      sharers: ""
    }

    this.getUser = this.getUser.bind(this);

  }
  

  getUser(user_id) {
    fetch('/api/twitter_user/' + user_id, {
      method: 'GET',
    }).then((res) => {
      res.json().then((responseJson) => {
        //console.log(responseJson);
        let new_sharers = this.state.sharers;
        new_sharers = new_sharers + responseJson.name;

        if (2 != this.props.sharers.length - 1) {
          new_sharers = new_sharers + ", "
        }
        this.setState({
          sharers: new_sharers
        });
      })
    }).catch(() => console.error('Error in fetching users'));
  }


  render() {
    let new_sharers = ""
    for (var sharer in this.props.sharers) {
      new_sharers = new_sharers + this.props.sharers[sharer];
      if (sharer != this.props.sharers.length - 1) {
          new_sharers = new_sharers + ", "
      }
    }





    return (
      <>
      <p>A link has: </p>
      <ul>
        <li>The link url: <a href={this.props.link}>{this.props.link}</a></li>
        <li>The number of people who shared it: {this.props.sharers.length}</li>
        <li>The names of the people who shared it: {new_sharers}</li>  
      </ul>
      
      
      
      </>
    )
  }

}



function App() {

  
  return (
    <LinkList/>
  );
}

export default App;
