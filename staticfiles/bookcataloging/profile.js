function submitForm() {
    const fileInput = document.getElementById('id_profile_picture');
    const file = fileInput.files[0];

    if (file) {
        console.log("File selected:", file.name); // debug

        const reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById('profile-pic-preview').src = e.target.result;
        }
        reader.readAsDataURL(file);
        document.getElementById('profile-pic-form').submit();
    } else {
        console.log("No file selected"); // debug

    }
}