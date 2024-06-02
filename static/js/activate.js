const qr = document.getElementById("qr")
// const goBtn = document.getElementById("goBtn")
const tokenInput = document.getElementById("token")
const overlay = document.getElementById("overlay")
const formActivate = document.getElementById("formActivate")

let validatedToken = null
async function goActivate(event) {
  event.preventDefault()
  const token = tokenInput.value
  const formData = new FormData(formActivate)
  overlay.style.display = "flex"

  try {
    const response = await fetch("/activateQR", {
      method: "POST",
      body: formData,
    })
    const responseData = await response.json()

    if (response.ok && responseData.status === "valid") {
      validatedToken = token
      generateQRCode()
      setInterval(generateQRCode, 5000)
      qr.style.display = "block"
      overlay.style.display = "none"
    } else {
      displayAlert(responseData.error_message || responseData)
      overlay.style.display = "none"
    }
  } catch (error) {
    console.error("Error:", error)
    displayAlert("Terjadi kesalahan dalam mengirim permintaan")
  }

  function displayAlert(responseData) {
    const { message, token } = responseData
    let alertTitle, alertIcon, alertText

    switch (message) {
      case "tidak lengkap":
        alertTitle = "Form tidak lengkap!"
        alertIcon = "error"
        alertText = "Mohon isi formulir dengan lengkap!"
        alertConfirm = true
        break
      case "Invalid token or password":
        alertTitle = "Token atau password anda salah!"
        alertIcon = "error"
        alertText = "Mohon isi formulir dengan benar!"
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
    }).then((result) => {
      if (result.isConfirmed) {
        window.location.href = "/activate"
      }
    })
  }
}

async function generateQRCode() {
  var qrcodeContainer = document.getElementById("qrcode")

  if (!qrcodeContainer) {
    console.error("QR code container not found")
    return
  }

  qrcodeContainer.innerHTML = ""

  var randomString = Math.random().toString(36).substring(2)
  try {
    new QRCode(qrcodeContainer, {
      text: randomString,
      width: 500,
      height: 500,
    })
  } catch (error) {
    console.error("Error generating QR code:", error)
    return
  }

  if (typeof validatedToken === "undefined" || !validatedToken) {
    console.error("Validated token is not defined or empty")
    return
  }

  try {
    const response = await fetch("/update_qr", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ token: validatedToken, qr_code: randomString }),
    })

    if (!response.ok) {
      const errorMessage = `Error: ${response.status} ${response.statusText}`
      console.error(errorMessage)
      displayAlert(errorMessage)
      return
    }

    const data = await response.json()

    if (data.success) {
      console.log("Success:", data)
    } else {
      console.error("Server error:", data)
      displayAlert(data.error_message || "Unknown error")
    }
  } catch (error) {
    console.error("Fetch error:", error)
    displayAlert("Terjadi kesalahan dalam mengirim permintaan")
  }
}

formActivate.addEventListener("submit", goActivate)
