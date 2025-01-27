import Document from "./Document"
import ChatBot from "./ChatBot"
import { useEffect } from "react";
function App() {

  useEffect(() => {
    const loginUser = async () => {
      try {
        const response = await fetch("/api/token_management", {
          method: "GET",
          redirect: 'follow',
          mode: "cors",
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/json"
          },
          credentials: 'omit'  // Add this line
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log(data.message); // Log the response from the backend
      } catch (error) {
        console.error(error);
      }
    };
  
    loginUser(); // Call the async function
  }, []);
  

  return (
    <>
    <div className="flex justify-center items-center">
      <div className="border-2 border-blue-600 w-3/5">
        <Document/>
      </div>
      <div className="w-2/5">
        <ChatBot/>
      </div>
    </div>
    </>
    
  )
}

export default App