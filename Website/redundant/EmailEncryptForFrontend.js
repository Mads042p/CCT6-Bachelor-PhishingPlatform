


                const derivedKey = await deriveKey(email, hashedPassword);
                const encryptedEmail = await encryptData(email, derivedKey);
                const iv = encryptedEmail.iv;
                
                const hex = Array.from(encryptedEmail.encryptedData)
                    .map(b => b.toString(16).padStart(2, "0"))
                    .join("");
            
                const decrypted = await decryptMessage(
                derivedKey,
                encryptedEmail.encryptedData,
                encryptedEmail.iv
                );
                const decoder = new TextDecoder("utf-8");
                


        function deriveKey(Email, hashedPassword){
            const encoder = new TextEncoder();
            const salt = encoder.encode(hashedPassword);
            const iterations = 10000;
            const keyMaterial = window.crypto.subtle.importKey(
                "raw",
                encoder.encode(Email),
                { name: "PBKDF2" },
                false,
                ["deriveKey"]
        );
            return keyMaterial.then((key) => {
                return window.crypto.subtle.deriveKey(
                    {
                        name: "PBKDF2",
                        salt: salt,
                        iterations: iterations,
                        hash: "SHA-256"
                    },
                    key,
                    { name: "AES-GCM", length: 256 },
                    false,
                    ["encrypt", "decrypt"]
                )
            });
        }
        

        async function encryptData(data, key) {
            const encoder = new TextEncoder();
            const iv = window.crypto.getRandomValues(new Uint8Array(12));
            
            return window.crypto.subtle.encrypt(
                {
                    name: "AES-GCM",
                    iv: iv
                },
                key,
                encoder.encode(data)
            ).then((encrypted) => {
                return { encryptedData: new Uint8Array(encrypted), iv: iv };
            });
        }

        async function decryptMessage(key, ciphertext, iv) {
            // The iv value is the same as that used for encryption
            return window.crypto.subtle.decrypt({ name: "AES-GCM", iv }, key, ciphertext);
    }
    
