// This file is ToroAI's  frontend chat interface.
// Workflow of this file is as follows : user question -> Flask /chat API -> RAG answer + sources -> display in chat.
// Includes session-only history, collapsible sidebar, PDF transcript download, and clickable sources.

"use client";

import { useState, useEffect, useRef } from "react";
import Image from "next/image";
import ReactMarkdown from "react-markdown";
import jsPDF from "jspdf";
import "./globals.css";

export default function Home() {

  // controls whether the sidebar is open or closed
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // stores what the user is typing in the input box
  const [question, setQuestion] = useState("");

  // stores all messages in the current conversation
  const [messages, setMessages] = useState([]);

  // shows whether ToroAI is currently waiting for an answer
  const [loading, setLoading] = useState(false);

  // controls whether the three-dot menu is open
  const [menuOpen, setMenuOpen] = useState(false);

  // stores previous chats only during the current browser session
  const [chats, setChats] = useState([]);

  // lets us detect clicks outside the sidebar
  const sidebarRef = useRef(null);

  // lets us detect clicks outside the three-dot menu
  const menuRef = useRef(null);


  // questions shown when the user has not started a conversation yet
  const suggestedQuestions = [
    "Can I travel while my CPT is pending?",
    "How do I apply for OPT?",
    "What is the difference between CPT and OPT?",
    "When should I start the STEM OPT process?",
    "Can I work on-campus as an F-1 student?"
  ];


  // closes the sidebar or dropdown when the user clicks somewhere outside them
  useEffect(() => {

    function handleClickOutside(event) {

      // close the three-dot menu if click happened outside of it
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target)
      ) {
        setMenuOpen(false);
      }

      // close the sidebar if click happened outside of it
      if (
        sidebarOpen &&
        sidebarRef.current &&
        !sidebarRef.current.contains(event.target)
      ) {
        setSidebarOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);

    // remove the event listener when the component is removed
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };

  }, [sidebarOpen]);


  // sends the user's question to the Flask backend API
  async function sendQuestion(selectedQuestion) {

    // suggested question is used if the user clicked one
    // otherwise use what the user typed
    const userQuestion = selectedQuestion || question;

    // do nothing if the question is empty
    if (userQuestion.trim() === "") {
      return;
    }


    // create the user's chat message
    const userMessage = {
      role: "user",
      text: userQuestion
    };


    // immediately display the user's message
    setMessages((oldMessages) => [
      ...oldMessages,
      userMessage
    ]);

    // clear the input box
    setQuestion("");

    // show loading message
    setLoading(true);


    try {

      // send the question to the ToroAI Flask backend
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/chat`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            question: userQuestion
          })
        }
      );


      // convert the JSON API response into JavaScript data
      const data = await response.json();


      // create ToroAI's message
      const toroMessage = {
        role: "assistant",
        text: data.answer,
        sources: data.sources
      };


      // add ToroAI's answer to the conversation
      setMessages((oldMessages) => [
        ...oldMessages,
        toroMessage
      ]);

    }

    catch (error) {

      // show an error message if frontend cannot reach backend
      const errorMessage = {
        role: "assistant",
        text: "Sorry, ToroAI could not connect to the backend."
      };

      setMessages((oldMessages) => [
        ...oldMessages,
        errorMessage
      ]);
    }


    // stop loading state
    setLoading(false);
  }


  // saves the current conversation into temporary session history
  function saveCurrentChat() {

    // do not save an empty conversation
    if (messages.length === 0) {
      return;
    }


    // find the first message written by the user
    const firstUserMessage = messages.find(
      (message) => message.role === "user"
    );


    // use the first user question as the chat title
    const chatTitle = firstUserMessage
      ? firstUserMessage.text.slice(0, 45)
      : "New Chat";


    // create the saved chat object
    const savedChat = {
      title: chatTitle,
      messages: messages
    };


    // add newest chat to the top of the sidebar history
    setChats((oldChats) => [
      savedChat,
      ...oldChats
    ]);
  }


  // starts a fresh chat
  function newChat() {

    // save current conversation before clearing it
    saveCurrentChat();

    // clear the current conversation
    setMessages([]);

    // clear the question box
    setQuestion("");

    // close dropdown menu if open
    setMenuOpen(false);
  }


  // opens an older chat from session history
  function openChat(chat) {

    // load saved messages back into the main chat area
    setMessages(chat.messages);

    // clear anything typed in the input box
    setQuestion("");
  }


  // ends the current chat
  function endChat() {

    // clear current messages
    setMessages([]);

    // clear input
    setQuestion("");

    // close menu
    setMenuOpen(false);
  }


  // downloads the current conversation as a PDF transcript
  function downloadTranscript() {

    // stop if there is no conversation to download
    if (messages.length === 0) {
      alert("No chat transcript to download.");
      return;
    }


    // create the PDF document
    const pdf = new jsPDF();

    // page measurements
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();

    const margin = 18;
    const maxWidth = pageWidth - margin * 2;

    // vertical position where text starts
    let y = 20;


    // PDF title
    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(18);

    pdf.text(
      "ToroAI Chat Transcript",
      margin,
      y
    );


    y += 9;


    // date and time
    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(10);

    pdf.text(
      `Generated: ${new Date().toLocaleString()}`,
      margin,
      y
    );


    y += 12;


    // line under the title
    pdf.line(
      margin,
      y,
      pageWidth - margin,
      y
    );


    y += 10;


    // go through every message in the current conversation
    messages.forEach((message) => {

      // check if we need a new page
      if (y > pageHeight - 30) {
        pdf.addPage();
        y = 20;
      }


      // decide whether the message belongs to the user or ToroAI
      const speaker =
        message.role === "user"
          ? "Student"
          : "ToroAI";


      // speaker name
      pdf.setFont("helvetica", "bold");
      pdf.setFontSize(12);

      pdf.text(
        `${speaker}:`,
        margin,
        y
      );


      y += 7;


      // clean Markdown characters for the PDF
      const cleanText = message.text
        .replace(/\*\*/g, "")
        .replace(/\*/g, "")
        .replace(/#/g, "");


      // wrap long text so it fits inside the PDF page
      const textLines = pdf.splitTextToSize(
        cleanText,
        maxWidth
      );


      // print message text
      pdf.setFont("helvetica", "normal");
      pdf.setFontSize(10);


      textLines.forEach((line) => {

        // create a new page if needed
        if (y > pageHeight - 20) {
          pdf.addPage();
          y = 20;
        }


        pdf.text(
          line,
          margin,
          y
        );


        y += 5.5;
      });


      // show sources for ToroAI messages
      if (
        message.sources &&
        message.sources.length > 0
      ) {

        y += 4;


        pdf.setFont(
          "helvetica",
          "bold"
        );

        pdf.text(
          "Sources:",
          margin,
          y
        );


        y += 6;


        pdf.setFont(
          "helvetica",
          "normal"
        );


        message.sources.forEach((source) => {

          // wrap long URLs
          const sourceLines = pdf.splitTextToSize(
            source,
            maxWidth
          );


          sourceLines.forEach((line) => {

            if (y > pageHeight - 20) {
              pdf.addPage();
              y = 20;
            }


            pdf.text(
              line,
              margin,
              y
            );


            y += 5;
          });

        });
      }


      // space between conversation messages
      y += 10;


      // divider between messages
      pdf.setDrawColor(220);

      pdf.line(
        margin,
        y,
        pageWidth - margin,
        y
      );


      y += 8;
    });


    // add footer to final page
    pdf.setFontSize(9);

    pdf.text(
      "Generated by ToroAI - CSUDH F-1 RAG Assistant",
      margin,
      pageHeight - 10
    );


    // download the PDF
    pdf.save(
      "ToroAI-chat-transcript.pdf"
    );


    // close the three-dot menu
    setMenuOpen(false);
  }


  return (

    <main className="app">


      {/* SIDEBAR */}
      <aside
        ref={sidebarRef}
        className={
          sidebarOpen
            ? "sidebar"
            : "sidebar sidebarClosed"
        }
      >


        {/* SIDEBAR OPEN / CLOSE BUTTON */}
        <button
          className="collapseButton"
          onClick={() =>
            setSidebarOpen(!sidebarOpen)
          }
        >
          {sidebarOpen ? "‹" : "›"}
        </button>


        {sidebarOpen && (

          <>

            {/* TOROAI LOGO */}
            <Image
              src="/toroai-logo.png"
              alt="ToroAI logo"
              width={230}
              height={100}
              className="sidebarLogo"
            />


            {/* NEW CHAT BUTTON */}
            <button
              className="newChatButton"
              onClick={newChat}
            >
              + New Chat
            </button>


            {/* SESSION CHAT HISTORY */}
            <div className="historySection">

              <h3>Recent Chats</h3>


              {/* show message when history is empty */}
              {chats.length === 0 && (

                <div className="emptyHistory">
                  No chats yet
                </div>

              )}


              {/* show saved chats */}
              {chats.map((chat, index) => (

                <div
                  key={index}
                  className="historyItem"
                  onClick={() => openChat(chat)}
                >
                  {chat.title}
                </div>

              ))}

            </div>

          </>

        )}

      </aside>



      {/* MAIN CONTENT */}
      <section className="mainContent">


        {/* THREE DOT MENU */}
        <div
          className="topMenu"
          ref={menuRef}
        >

          <button
            className="menuButton"
            onClick={() =>
              setMenuOpen(!menuOpen)
            }
          >
            ⋮
          </button>


          {menuOpen && (

            <div className="menuDropdown">

              {/* DOWNLOAD CURRENT CHAT AS PDF */}
              <button
                onClick={downloadTranscript}
              >
                Download transcript
              </button>


              {/* END CURRENT CHAT */}
              <button
                className="endChatButton"
                onClick={endChat}
              >
                End chat
              </button>

            </div>

          )}

        </div>



        {/* HEADER */}
        <div className="hero">

          <Image
            src="/toroai-logo.png"
            alt="ToroAI logo"
            width={300}
            height={130}
            className="mainLogo"
          />


          <div className="descriptionBox">

            A RAG-powered chatbot built to answer international students&apos;{" "}

            <strong>
              F-1, CPT, OPT
            </strong>

            , and related immigration & academic queries.

          </div>

        </div>



        {/* SUGGESTED QUESTIONS */}
        {messages.length === 0 && (

          <div className="suggestedSection">

            <h3>
              💡 Suggested Questions
            </h3>


            <div className="suggestedGrid">

              {suggestedQuestions.map(
                (item, index) => (

                  <button
                    key={index}
                    className="suggestedCard"
                    onClick={() =>
                      sendQuestion(item)
                    }
                  >
                    {item}
                  </button>

                )
              )}

            </div>

          </div>

        )}



        {/* CHAT AREA */}
        <div className="chatArea">

          {messages.map(
            (message, index) => (

              <div
                key={index}
                className={
                  message.role === "user"
                    ? "messageRow userRow"
                    : "messageRow assistantRow"
                }
              >


                {/* TOROAI AVATAR */}
                {message.role === "assistant" && (

                  <Image
                    src="/toro-mascot.png"
                    alt="ToroAI mascot"
                    width={52}
                    height={52}
                    className="assistantAvatar"
                  />

                )}


                {/* MESSAGE BOX */}
                <div
                  className={
                    message.role === "user"
                      ? "userMessage"
                      : "assistantMessage"
                  }
                >


                  {/* TOROAI NAME */}
                  {message.role === "assistant" && (

                    <div className="assistantName">
                      ToroAI
                    </div>

                  )}


                  {/* MESSAGE TEXT WITH MARKDOWN */}
                  <div className="messageText">

                    <ReactMarkdown>
                      {message.text}
                    </ReactMarkdown>

                  </div>


                  {/* CLICKABLE SOURCES */}
                  {message.sources &&
                    message.sources.length > 0 && (

                      <div className="sources">

                        <h4>Sources</h4>


                        {message.sources.map(
                          (source, sourceIndex) => (

                            <a
                              key={sourceIndex}
                              href={source}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="sourceLink"
                            >
                              {source}
                            </a>

                          )
                        )}

                      </div>

                    )}

                </div>

              </div>

            )
          )}


          {/* LOADING MESSAGE */}
          {loading && (

            <div className="loading">
              ToroAI is thinking...
            </div>

          )}

        </div>



        {/* QUESTION INPUT */}
        <div className="inputArea">

          <input
            type="text"
            value={question}
            placeholder="Ask your F-1 / CPT / OPT question..."
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            onKeyDown={(event) => {

              if (event.key === "Enter") {
                sendQuestion();
              }

            }}
          />


          {/* SEND BUTTON */}
          <button
            className="sendButton"
            onClick={() =>
              sendQuestion()
            }
          >
            ➤
          </button>

        </div>



        {/* FOOTER MESSAGE */}
        <div className="footerMessage">

          ✨ Thank you for using{" "}

          <strong>
            ToroAI!
          </strong>

          {" "}We&apos;re here to help. ✨

        </div>


      </section>

    </main>
  );
}