import React from 'react'

import logo from './logo.svg';
import './App.css';


class LinkList extends React.Component {
  render() {
    let linksArray = [];
    let sharers1 = ["Andrew", "Jane"]
    let sharers2 = ["Bob"]
    linksArray.push(<Link link="meow.com" sharers={sharers1}/>);
    linksArray.push(<Link link="squirrel.edu" sharers={sharers2}/>);
    linksArray.push(<Link link="nice.cool" sharers={sharers2}/>);

    



    return (
      <div>
        {linksArray}
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
  
  fetch('/user/1/following_tweets', {
    method: 'GET',
  }).then((res) => {
    res.text().then((responseText) => {
      console.log(responseText);
    })
  }).catch(() => console.error('Error in fetching tweets'));
  
  return (
    <LinkList/>
  );
}

export default App;
