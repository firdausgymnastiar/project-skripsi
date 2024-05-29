const formGenerate = document.getElementById("formGenerate")

function generateRandomNumber() {
  const randomNumber = Math.floor(100000 + Math.random() * 900000)
  console.log("Angka acak: " + randomNumber)
  document.getElementById("randomNumberDisplay").value = randomNumber
}

async function sendToServer() {
  const formData = new FormData(formGenerate)
  document.getElementById("overlay").style.display = "flex"

  try {
    const response = await fetch("/generatetoken", {
      method: "POST",
      body: formData,
    })
    const responseData = await response.json()

    if (response.ok && responseData.success) {
      displayAlert(responseData)
    } else {
      displayAlert(responseData.error_message || responseData)
    }
  } catch (error) {
    console.error("Error:", error)
    displayAlert("Terjadi kesalahan dalam mengirim permintaan")
  }
}

formGenerate.addEventListener("submit", function (event) {
  event.preventDefault()
  sendToServer()
})

function displayAlert(responseData) {
  const { message, token } = responseData
  let alertTitle, alertIcon, alertText

  switch (message) {
    case "successfull":
      alertTitle = "Token Berhasil Diaktifkan!"
      alertIcon = "success"
      alertText = `Token Anda Adalah: <strong id="token">${token}</strong> <button id="copy-btn" type="button" class="btn btn-success btn-sm">Copy</button>`
      alertConfirm = false
      break
    case "token is existing":
      alertTitle = "Token Sudah Ada!"
      alertIcon = "error"
      alertText = "Maaf token sudah ada, mohon generate ulang!"
      alertConfirm = true
      break
    case "form kosong":
      alertTitle = "Formulir tidak lengkap!"
      alertIcon = "error"
      alertText = "Mohon isi formulir dengan lengkap!"
      alertConfirm = true
      break
    default:
      alertTitle = "Error!"
      alertIcon = "error"
      alertText = message
      alertConfirm = true
      break
  }

  Swal.fire({
    icon: alertIcon,
    title: alertTitle,
    html: alertText,
    allowOutsideClick: false,
    showConfirmButton: alertConfirm,
    didRender: () => {
      const copyButton = document.getElementById("copy-btn")
      if (copyButton) {
        copyButton.addEventListener("click", () => copyTokenToClipboard(token))
      }
    },
  }).then((result) => {
    if (result.isConfirmed) {
      window.location.href = "/generate"
    }
  })
}

function copyTokenToClipboard(token) {
  const textarea = document.createElement("textarea")
  textarea.value = token
  document.body.appendChild(textarea)
  textarea.select()
  document.execCommand("copy")
  document.body.removeChild(textarea)

  Swal.fire({
    icon: "success",
    title: "Copied!",
    text: "Token telah disalin ke clipboard.",
    allowOutsideClick: false,
    showConfirmButton: true,
  }).then((result) => {
    if (result.isConfirmed) {
      window.location.href = "/generate"
    }
  })
}
