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
    fetch('/user/1/following_tweets?urls_only=true', {
      method: 'GET',
    }).then((res) => {
      res.json().then((responseJson) => {
        console.log(responseJson);
        this.setState(
          {
            links: responseJson
          }
        )
      })
    }).catch(() => console.error('Error in fetching tweets'));
  }
  
  
  
  render() {
    
    //this.getLinks();

    let linksArray = [];
    let linksDict = {};
    for (let link in this.state.links) {
      //console.log(this.state.links[link]);

      if (this.state.links[link].url in linksDict) {
        console.log(linksDict[this.state.links[link].url]);
        let sharers = linksDict[this.state.links[link].url];
        sharers.push(this.state.links[link].twitter_user_id)
        linksDict[this.state.links[link].url] = sharers;

      } else {
        //console.log(this.state.links[link].url);
        linksDict[this.state.links[link].url] = [this.state.links[link].twitter_user_id];
      }
      //console.log(linksDict);
      

      //check if the url is already in the links dictionary
      //if yes:
      //  add to sharers
      //if no:
      //  create a new link with sharers of the twitter_user_id for now, eventually connect to get the twitter user name from the background 

    }

    for (let new_link in linksDict) {
      linksArray.push(<Link link={new_link} sharers={linksDict[new_link]}/>);
    }




    //let linksArray = [];
    //let sharers1 = ["Andrew", "Jane"]
    //let sharers2 = ["Bob"]
    //linksArray.push(<Link link="meow.com" sharers={sharers1}/>);
    //linksArray.push(<Link link="squirrel.edu" sharers={sharers2}/>);
    //linksArray.push(<Link link="nice.cool" sharers={sharers2}/>);

    



    return (
      <div>
        {linksArray}
        <button type="button" onClick={this.getLinks}>Refresh</button>
      </div>
    )
  }
}

class Link extends React.Component {
  render() {

    let sharers = "";

    for (var sharer in this.props.sharers) {
      sharers = sharers + this.props.sharers[sharer];
      if (sharer != this.props.sharers.length - 1) {
          sharers = sharers + ", "
      }
    }



    return (
      <>
      <p>A link has: </p>
      <ul>
        <li>The link url: <a href={this.props.link}>{this.props.link}</a></li>
        <li>The number of people who shared it: {this.props.sharers.length}</li>
        <li>The names of the people who shared it: {sharers}</li>  
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
