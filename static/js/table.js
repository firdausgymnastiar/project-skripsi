const detail = document.getElementById("detail")
const goBtn = document.getElementById("goBtn")
const tokenInput = document.getElementById("token")
const overlay = document.getElementById("overlay")

async function goDetail() {
  const token = tokenInput.value

  overlay.style.display = "flex"

  const response = await fetch("/generatetable", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ tokenKelas: token }),
  })

  const responseDataKelas = await response.json()
  if (response.ok && responseDataKelas.status === "valid") {
    overlay.style.display = "none"
    detail.style.display = "block"
  } else {
    alertTable(responseDataKelas)
  }
}

function alertTable(responseDataKelas) {
  let message = responseDataKelas.message

  let alertTitle, alertIcon, alertText

  switch (message) {
    case "valid":
      alertTitle = "Kelas Valid!"
      alertIcon = "success"
      alertText = "token anda valid"
      break
    case "token tidak valid":
      alertTitle = "Token Anda Tidak Valid!"
      alertIcon = "error"
      alertText = "Mohon ulangi dengan token yang valid"
      break
    case "token kosong":
      alertTitle = "Token Kosong!"
      alertIcon = "error"
      alertText = "Harap masukan token terlebih dahulu"
      break
    default:
      alertTitle = "Error!"
      alertIcon = "error"
      alertText = message
      break
  }
  Swal.fire({
    icon: alertIcon,
    title: alertTitle,
    text: alertText,
    allowOutsideClick: false,
  }).then((result) => {
    if (result.isConfirmed) {
      // window.location.href = "/login"
      overlay.style.display = "none"
    }
  })
}
goBtn.addEventListener("click", goDetail)
