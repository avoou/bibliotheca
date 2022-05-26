document.addEventListener('DOMContentLoaded', function(){
               

    let form_button = document.querySelector('input[type=submit]')
    form_button.addEventListener('click', async function (event){
        console.log('sdfvsvdsdv')
        //event.preventDefault();
        let all_inputs = document.querySelectorAll("input[class=text_input]")
        let input_username = all_inputs[0]
        let input_name = all_inputs[1]
        let input_password = all_inputs[2]
        
        if (input_username.checkValidity() && input_name.checkValidity() && input_password.checkValidity()) {
            event.preventDefault();
            let response = await fetch("/registration", {
                headers: {'Content-Type': 'application/json'},
                method: "POST",
                body: JSON.stringify({
                    email: input_username.value,
                    name: input_name.value, 
                    password: input_password.value,
                })
            });
        
            let response_json = await response.json()
            console.log(response.ok)
            if  (response.ok) {
                div_mainbox= document.querySelector('div[name=main_box]')
                div_mainbox.innerHTML = `<div name="message">
                                            Hello, 
                                                <h3 style="display: inline-block;">
                                                    <div name="uname" style="display: inline-block;"></div>!
                                                </h3>
                                            </br>
                                            You have successfully registered</br>
                                            Loading ...
                                        </div>`
                username = div_mainbox.querySelector('div[name=uname]')
                username.innerText = response_json.name
                setTimeout(function(){document.location.href = "/"}, 1500);
                
            } else {
                let warning_message = document.querySelector('div[name=registration_false_warning]')
                warning_message.style.textAlign = "center"
                warning_message.innerText = response_json.detail
                warning_message.style.color = "red"}
        } 
    }) 
})