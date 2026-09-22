# Lecture 12 — Information Security

> **Question for today** — How do we trust a party whose face we cannot see?

*Figure labels are in Japanese; the captions here translate them.*

## Learning goals

- Name the three elements of information security and give an example of each being broken
- Explain the difference between symmetric and public-key cryptography, and the advantages and limits of each
- Explain the roles of hash functions and digital signatures
- Explain how certificates and certification authorities build a "chain of trust"
- Distinguish authentication from authorisation, and explain multi-factor authentication, passkeys and single sign-on
- Explain the representative attack techniques and why they succeed
- Explain the effect of quantum computers on public-key cryptography, and why migration is under way now

## Time allocation

| Minutes | Content |
| --- | --- |
| 0–5 | Review of last time |
| 5–12 | 12.1 What we are protecting |
| 12–37 | 12.2 The basics of cryptography |
| 37–50 | 12.3 Certificates and the chain of trust |
| 50–67 | 12.4 Authentication and authorisation |
| 67–85 | 12.5 Real-world threats |
| 85–90 | Exercises and summary |

---

## 12.1 What we are protecting

### The three elements of information security

| Element | Content | Example of it being broken |
| --- | --- | --- |
| **Confidentiality** | Not shown to those without permission | A leak of personal information |
| **Integrity** | Not rewritten without permission | Defacement of a website, unauthorised alteration of grade data |
| **Availability** | Usable when needed | Denial of service attacks, encryption by ransomware |

Taking the initials gives **CIA** (no relation to the intelligence agency).

These three often **conflict with each other**. To maximise confidentiality, the
safest course is to show it to nobody, switch off the power and unplug it from the
network — but then availability is lost. **Security is not "making things safe" but
"deciding the balance between what must be protected and the convenience that may
be given up".**

In recent years **authenticity** (that the party is who they claim to be) and
**non-repudiation** (that one cannot later say "I did not do it") are often added to
the discussion.

### The difference between face-to-face and remote

Consider a transaction in person.

- You can see the other party's face. The shop exists
- Cash and goods are exchanged on the spot
- If something goes wrong you can go to the shop

On the internet all of this is lost.

| In person | On the internet |
| --- | --- |
| You confirm the other party with your eyes | **You do not know who the other party is** |
| You exchange on the spot | You do not know whether what you sent arrived |
| The conversation is heard only by the parties | **Anyone along the path can listen** |
| You sign a contract | The signature can be imitated |

As we saw in Lectures 9 and 10, packets pass through many networks. **Somewhere
along the path the content can be read, and it can be rewritten.**

Hence the need for cryptography.

---

## 12.2 The basics of cryptography

### Vocabulary

| Term | Meaning |
| --- | --- |
| Plaintext | The original data |
| Ciphertext | The encrypted data |
| Encryption / decryption | Plaintext→ciphertext / ciphertext→plaintext |
| Key | The secret value used for encryption and decryption |

**Kerckhoffs's principle** (1883) is the premise of modern cryptography.

> Even with the cipher itself published, it must be **secure so long as the key is
> secret**.

"Maintaining security by keeping the method secret" (security by obscurity) does
not work. The method will leak eventually, and it is precisely the method that has
been published and survived attack by many researchers that can be trusted. The
practical iron rule that **you must not use a cipher of your own invention** comes
from this.

### Symmetric cryptography

Uses **the same key** for encryption and decryption.

- Processing is **fast** (it can handle large volumes of data)
- Representative: AES (the current standard), ChaCha20

**The problem is key distribution.**

> To hand a key safely to the other party requires a secure channel.
> But making a secure channel requires a key.

It goes in circles.

Furthermore, n people communicating with each other require n(n−1)/2 keys. For 100
people, 4,950; for 10,000, about 50 million. Unmanageable.

### Public-key cryptography

Diffie–Hellman in 1976 and RSA in 1977 broke this impasse.

**Split the key in two.**

**What is encrypted with the public key can only be decrypted with the
corresponding private key.**

> **[Figure 12-1] Sending a secret with public-key cryptography**
> Sender on the left, recipient on the right.
> (1) The recipient publishes their public key (arrow to the left, drawn as an open
>     padlock)
> (2) The sender encrypts the plaintext with that public key (closing the padlock)
> (3) The ciphertext is sent (an eavesdropper is drawn on the path, unable to read it)
> (4) The recipient decrypts with the private key (opening it with a key)
> Drawn so that the metaphor comes across: "anyone can close the padlock, but only
> the person with the key can open it".

![Figure 12-1 Sending a secret with public-key cryptography](../figures/fig-12-01.svg)

**The key distribution problem is solved.** The public key may be stolen, so it can
be distributed over an insecure channel. And n people need only 2n keys.

**Why the private key cannot be guessed.** It rests on mathematical problems that
are easy to compute in one direction but not computable in any practical time in
reverse.

- **RSA** — multiplying two large primes is easy, but factorising the product is hard
- **Elliptic-curve cryptography (ECC)** — the discrete logarithm problem on an
  elliptic curve. Equivalent strength with a shorter key than RSA

**The connection to Lecture 2**: this is a question of complexity. Factorisation is
not "uncomputable"; it is merely that no algorithm solving it in polynomial time is
known. If P = NP were proved and an efficient algorithm found, today's public-key
cryptography would be powerless overnight. **The security of cryptography rides not
on mathematical proof but on the fact that nobody has solved it yet.**

### Quantum computers undermine that fact

As we saw in Lecture 1, quantum computers do not change **the range of what can be
computed** but do change **speed**. And public-key cryptography is squarely among
what changes.

**Shor's algorithm** (1994) solves factorisation and the discrete logarithm in
polynomial time. That is, **it breaks both RSA and elliptic-curve cryptography** —
essentially all of today's public-key cryptography.

The effect on symmetric cryptography (AES), by contrast, is small. Even with
Grover's algorithm the search only falls to √n, so doubling the key length restores
the original strength. For hash functions, lengthening the output suffices. **The
impact is concentrated on public-key cryptography.**

### "There are no quantum computers yet, so we are fine" is wrong

Practical quantum computers do not exist as of 2026. Migration is nonetheless being
hurried, **because the attack works from today**.

> **Intercept the traffic now and store it; decrypt it once a quantum computer
> exists.**

This is **store now, decrypt later**. What you encrypt and send today is read in
ten years. **Data that must remain secret for a long time is already exposed.**
Communications handling medical records or state secrets cannot wait for quantum
computers to be completed.

So migration is under way to **post-quantum cryptography** (PQC), based on
mathematical problems that quantum computers are not known to solve efficiently
either (lattice problems and others). NIST in the United States settled standards
in 2024 (**ML-KEM** for key exchange, **ML-DSA** for signatures, and others).

**The migration is being done as a hybrid.** In TLS, the conventional key exchange
and the PQC key exchange are both run and the results combined. If one is broken
the other survives, and it insures against the new scheme turning out to be weak.
As of 2026, this hybrid key exchange is enabled in the major browsers and servers.

NIST's selection was made by open call and public analysis, and candidates broken
along the way were dropped. **It is an example of Kerckhoffs's principle from the
start of 12.2 being put into practice exactly.**

### The hybrid approach

Public-key cryptography is **slow** — hundreds to thousands of times the
computation of symmetric cryptography. It cannot be used for large volumes of data.

So in practice the two are combined.

```
1. Hand over a "symmetric key" safely using public-key cryptography
   (a small amount of data, so slowness is no problem)
2. Encrypt the subsequent traffic with that symmetric key (fast)
```

**TLS (Lecture 10) does exactly this.** The initial handshake uses public-key
cryptography to share a symmetric key, and the subsequent traffic flows under
symmetric encryption.

### Hash functions

A **hash function** produces a fixed-length value (a hash, a digest) from data of
arbitrary length.

The properties it must satisfy:

| Property | Content |
| --- | --- |
| One-wayness | The original data cannot be obtained from the hash |
| Collision resistance | Different data giving the same hash cannot be found |
| Avalanche effect | Changing one bit of the input changes the output greatly |

**Uses**:

- **Detecting tampering** — hold the data and the hash separately and compare
- **Storing passwords** — store the hash rather than the password itself. Even if
  leaked, the original password is unknown
- **Digital signatures** — see below

**What may be used**: SHA-256, SHA-3.
**What must not be used**: MD5, SHA-1 (collisions have actually been found).

**Use a dedicated function for storing passwords.** SHA-256 is designed to be fast,
which also makes brute-force attacks fast. For passwords, use the **deliberately
slow** bcrypt, scrypt or Argon2, and mix in a per-user value (a salt) so that the
same password does not give the same hash.

### Digital signatures

Use public-key cryptography **in reverse**.

> **What has been processed with a private key can be verified with the
> corresponding public key.**

Only the owner holds the private key, so it can be shown that **only they could
have produced it**.

```
The signing side:
  1. Compute the hash of the document
  2. Process the hash with your own private key = the signature
  3. Send the document and the signature

The verifying side:
  1. Compute the hash of the document received
  2. Process the signature with the sender's public key
  3. If 1 and 2 agree, then "the owner signed it" and "the document has not been altered"
```

> **[Figure 12-2] Producing and verifying a digital signature**
> Above, producing the signature: document → (hash function) → hash → (private key)
> → signature. Below, verification: the received document → (hash function) → hash
> A; the received signature → (public key) → hash B; then the comparison of A and B.
> A branch shows "authentic and intact" if they agree, "altered or forged" if not.

![Figure 12-2 Producing and verifying a digital signature](../figures/fig-12-02.svg)

This gives **integrity** and **non-repudiation**.

**Note the difference between encryption and signing.** A signature does not keep
the document secret (anyone can read it). To keep it secret, do both.

---

## 12.3 Certificates and the chain of trust

### The problem that remains

Public-key cryptography solved key distribution. But a hole remains.

> **Is that public key really the other party's?**

If an attacker hands over a false key saying "this is the bank's public key", the
user encrypts with it and the attacker can read it. This is a
**man-in-the-middle attack**.

Even with encryption, **it is meaningless if the party you encrypted to is a
fake**. This is what Lecture 10 meant by "of TLS's three guarantees, authenticity
is the foundation".

### Public-key certificates

The solution is to **have a trusted third party vouch that "this public key really
belongs to this person"**.

A **public-key certificate** (an X.509 certificate) contains the following.

| Item | Content |
| --- | --- |
| Subject name | Whose certificate it is (for a server, the FQDN, e.g. `www.example.com`) |
| Public key | That subject's public key |
| Issuer | Who is vouching |
| Validity period | From when until when |
| Usage | What it may be used for |
| **Issuer's signature** | A signature by the issuer's private key |

The last, the issuer's signature, is the crux. Alter even one bit of the
certificate's contents and verification of the signature fails.

### Certification authorities and the chain of trust

The body that issues certificates is a **certification authority** (CA).

But how do we confirm that the CA's public key is genuine? The same problem
reappears. Here a **chain** is used.

> **[Figure 12-3] The chain of trust of certificates**
> Stacked from the bottom: "server certificate (www.example.com)", "intermediate CA
> certificate", "root CA certificate", with upward arrows showing that the lower
> certificate is signed by the upper one's private key. The root CA certificate at
> the top is **self-signed**, and that it is built into the browser/OS in advance is
> expressed by a box labelled "trust store" enclosed in dotted lines. A note on the
> right gives the flow of the judgement: verification proceeds from the bottom
> upwards, succeeding on reaching the trust store and warning if it does not.

![Figure 12-3 The chain of trust of certificates](../figures/fig-12-03.svg)

1. The server certificate is signed by the intermediate CA's private key
2. The intermediate CA's certificate is signed by the root CA's private key
3. **The root CA's certificate is self-signed**, and **is built into the browser and
   OS in advance**

So the ultimate basis of trust is that **the developer of the browser or OS judged
this CA to be trustworthy**.

### The weakness of this arrangement

**The starting point of trust is spread across hundreds of CAs.** Browsers have
hundreds of CAs from around the world registered, and **if any one of them issues a
fraudulent certificate, any site can be impersonated.**

Cases that have actually occurred:

- In 2011 a Dutch CA was compromised and false certificates for Google among others
  were issued. That CA was removed from the trust lists and ceased business
- Cases of governments and companies forcibly installing their own CA on devices
  and using it to intercept traffic

**Mechanisms introduced as countermeasures**:

- **Certificate Transparency** — every certificate issued is recorded in a public
  log. A domain owner can detect a certificate they did not ask for
- **Revocation checking** — a mechanism to invalidate compromised certificates (OCSP
  and others)
- **Shorter validity periods** — a few months at most. Even if revocation fails to
  work, the window of damage is limited

### Do not ignore a certificate warning

A browser warns "this connection is not secure" when one of the following is
happening.

- The name in the certificate does not match the domain being accessed
- It has expired
- No trusted CA can be reached (including self-signed certificates)
- It has been revoked

**None of these can be distinguished from what happens under a man-in-the-middle
attack.** Clicking through with "it is probably a misconfiguration" is the same
operation as letting an attack through.

---

## 12.4 Authentication and authorisation

### Distinguishing them

They are often confused but are entirely different concepts.

| | Authentication | Authorisation |
| --- | --- | --- |
| The question | **Who are you?** | **What may you do?** |
| Example | Logging in | Permission to read and write a file |
| Order | First | Second |

"Confirmed to be who they are" and "allowed to perform that operation" are
different. A student who has logged in correctly is still not entitled to rewrite
someone else's grades.

**Many real incidents are failures of authorisation.** A login function is built,
but defects of the sort "rewrite the ID in the URL and you can see someone else's
data" are found again and again.

### The three factors of authentication

| Factor | Content | Examples |
| --- | --- | --- |
| **Knowledge** (something you know) | Something you know | Password, PIN |
| **Possession** (something you have) | Something you hold | Smartphone, IC card, security key |
| **Inherence** (something you are) | A physical characteristic | Fingerprint, face, iris |

**Multi-factor authentication (MFA)** combines two or more **different factors**.
"Password + secret question" is not multi-factor, since both are knowledge.

**Why it is effective**: a password can leak (reuse, phishing, exfiltration from a
server). But it is hard for an attacker to obtain the user's smartphone remotely.
The point is **combining factors whose attacks are of different natures**.

### The limits of passwords

Passwords have structural problems.

- There is a limit to the complexity one can remember
- They are reused (one leak spreads to every service)
- **They are weak against phishing** — enter it on a fake site and it is over
- They leak on the server side

**An SMS confirmation code does not fully prevent phishing either.** If the fake
site extracts the code from the user and enters it on the real site immediately, it
gets through.

### Passkeys (FIDO2 / WebAuthn)

A **passkey** uses public-key cryptography for authentication.

```
At registration:
  1. The user's device generates a key pair
  2. The public key is registered with the server. The private key never leaves the device

At authentication:
  3. The server sends a random value (a challenge)
  4. The device signs it with the private key and returns it
  5. The server verifies with the registered public key
```

**Why it is resistant to phishing in principle**: **the domain name being accessed**
is included in what is signed. In response to a request from the fake site
`examp1e.com`, the device does not sign with the key for `example.com`. **Even if
the user is deceived, the device is not.**

Further, only the public key is stored on the server, so authentication credentials
do not leak even if the server is compromised.

Use of the private key requires unlocking the device (biometrics or a PIN). This
establishes the multiple factors of "possession" and "knowledge/inherence"
naturally.

### Consolidating authentication

As the number of machines and services grows, managing a separate account for each
breaks down.

| Approach | Content |
| --- | --- |
| **Directory service** | Centralised management of user information (LDAP, Active Directory) |
| **Single sign-on (SSO)** | One authentication gives access to several services |
| **Federation** | Passing authentication information across organisations (SAML, GakuNin Shibboleth) |

(**NIS**, once used on Unix systems, is not used today because its communication is
unencrypted and insecure.)

### OAuth 2.0 and OpenID Connect

Two things commonly used on the modern web, to be distinguished.

| | Purpose |
| --- | --- |
| **OAuth 2.0** | **Authorisation**. "Allow this app to read my calendar, and nothing else" |
| **OpenID Connect** | **Authentication**. Built on OAuth 2.0. Conveys "who this person is" |

**The point of OAuth is not handing over your password.** Instead of telling an
external application your password, you give it **a token with limited
permissions**.

- Permissions can be narrowed (read only, a particular scope only)
- An expiry can be set
- It can be revoked later
- You need not change your password

Behind the "log in with ..." button is OpenID Connect.

---

## 12.5 Real-world threats

### The main attack techniques

| Attack | Content | Main countermeasures |
| --- | --- | --- |
| **Phishing** | Lure to a fake site and have information entered | Passkeys, checking the domain, education |
| **Malware** | Execution of malicious software | Applying updates, restricting execution |
| **Ransomware** | Encrypt data and demand a ransom | **Offline backups**, cutting the route of entry |
| **SQL injection** | Embed SQL in an input value for unauthorised operations | Use placeholders |
| **Cross-site scripting (XSS)** | Execute malicious JS in another person's browser | Escape on output |
| **Buffer overflow** | Seize control by writing beyond a region | Memory-safe languages, bounds checking |
| **Man-in-the-middle** | Interpose on the communication path | TLS and certificate verification |
| **DDoS** | Stop a service with a flood of traffic | CDN, rate limiting |
| **Supply chain attack** | Enter via a library or supplier in use | Knowing and verifying dependencies |

### The common structure by which attacks succeed

The individual techniques differ, but **the same structure** lies beneath them.

**(1) The boundary between data and code is blurred**

As we saw in Lecture 3, a von Neumann machine places instructions and data without
distinction. That design makes the following attacks possible.

- SQL injection — input intended as **data** is interpreted as **part of the SQL**
- XSS — input intended as **data** is executed as **JavaScript**
- Buffer overflow — a write of **data** rewrites the **return address**
  (see the memory layout of Lecture 4)

**The common countermeasure is to treat data as data.** Rather than assembling SQL
by concatenating strings, use placeholders to state explicitly "this is a value".

```python
# dangerous: the input can be interpreted as SQL
cursor.execute("SELECT * FROM users WHERE name = '" + name + "'")

# safe: it is treated as a value
cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
```

**(2) Trust is placed in the wrong place**

- Believing only client-side validation (the user can modify it)
- Assuming "it is the internal network, so it is safe"
- Assuming the input is in the correct format

**(3) The human being is the weakest**

However firmly the technical defences are built, if the user enters their password
on a fake site it is breached. That is why designs in which **no harm results even
when the human is deceived** (such as passkeys) matter.

### Devices for performance become holes

**Spectre and Meltdown** (2018), touched on in Lecture 5, abuse speculative
execution, a mechanism for improving performance.

Execution on a wrong prediction is cancelled, but **the trace left in the cache is
not erased**. By measuring differences in access time, the contents of memory that
should not be readable can be inferred.

This was not an implementation bug; the cause was **the design for performance
itself**. The only options were to change the CPU design or to introduce
countermeasures that sacrifice performance, and the impact was wide.

**The lesson**: a layer of abstraction sometimes leaks "the circumstances of the
layer below" for the sake of performance. That leak can become a leak of
information.

### Zero trust

Conventional defence was **perimeter-based**. It thought "inside the internal
network is safe, outside is dangerous" and put a firewall at the boundary.

Why this stopped working:

- With cloud use, assets no longer sit inside the organisation (Lecture 8)
- With remote working, users are not inside the organisation
- Once penetrated, an attacker moves freely inside

**Zero trust** changes the premise.

> **Trust nothing, regardless of position in the network. Verify every access,
> every time.**

- Authenticate the user and the device every time
- Grant only the minimum necessary permissions (the principle of least privilege)
- Record every access and detect anomalies
- Segment the network finely to limit the blast radius of an intrusion

### Principles for the defending side

| Principle | Content |
| --- | --- |
| Defence in depth | If one defence is breached, there is another |
| Least privilege | Grant only the permissions needed, only for as long as needed |
| Fail safe | On an anomaly, deny (the same idea as the response to undecidability in Lecture 1) |
| Do not rely on obscurity | Kerckhoffs's principle |
| Apply updates | Known vulnerabilities account for most attacks |
| **Backups** | Being able to recover is the last line. Keep an offline copy (Lecture 6) |
| Keep records | So that what happened can be traced afterwards |

**Security is a process, not a product.** It is not configured once and finished;
both the threats and the environment keep changing.

---

## Exercises

> **Submission**: through Moodle. For **essay questions**, write out your reasoning
> and working. For **numerical and cloze questions**, enter only the answer (no
> working needed).

**12-1.** Name the three elements of information security, and state concretely
what would happen in a university grade system if each were broken.

**12-2.** What is the key distribution problem in symmetric cryptography? Find the
number of keys needed for n people to communicate with each other, for symmetric
and for public-key cryptography, and compare them at n=1000.

**12-3.** Why does TLS use both symmetric and public-key cryptography? Explain where
each is used.

**12-4.** Describe the procedure for verifying a digital signature, and give two
things that are guaranteed when verification succeeds.

**12-5.** Give three cases in which a browser issues a certificate warning. Also
explain why it is dangerous to ignore the warning and connect.

**12-6.** Explain the difference between authentication and authorisation, and give
an example of a system in which "authentication is performed correctly but
authorisation is defective".

**12-7.** Explain why a passkey is more resistant to phishing than a password plus
SMS authentication, with reference to what is included in what is signed.

**12-8.** The following code has an SQL injection vulnerability. Explain what an
attacker would enter for `name` and what would happen, and fix it.

```python
name = request.get("name")
cursor.execute("SELECT * FROM users WHERE name = '" + name + "'")
```

**12-9.** Practical quantum computers do not yet exist, so why is migration to
post-quantum cryptography being hurried? Explain with reference to "store now,
decrypt later". Also state why the magnitude of the effect differs between
symmetric and public-key cryptography.

**12-10.** What is the most important preparation for minimising the damage of
ransomware? Explain with reference to Lecture 6.

---

## Summary

- Security is deciding the balance among confidentiality, integrity and availability
- By Kerckhoffs's principle, design on the premise that the method is public. Do
  not use a cipher of your own invention
- Symmetric cryptography is fast but has the key distribution problem. Public-key
  cryptography solved that but is slow. In practice they are used as a hybrid
- The security of public-key cryptography depends not on mathematical proof but on
  "nobody has solved it yet"
- Quantum computers break RSA and elliptic-curve cryptography via Shor's algorithm.
  The effect on symmetric cryptography is small; the impact is concentrated on
  public-key cryptography
- Because "intercept now, decrypt later" works, migration to post-quantum
  cryptography is under way without waiting for quantum computers to be completed.
  In TLS it is used alongside the conventional scheme as a hybrid
- Digital signatures bring integrity and non-repudiation
- Certificates and CAs build a "chain of trust", but have the weakness that the
  starting point is spread across hundreds of CAs
- Authentication and authorisation are different things. Many incidents are failures
  of authorisation
- Passkeys are resistant to phishing in principle, because even when the user is
  deceived the device is not
- Most major attacks derive from the blurred boundary between data and code
- Perimeter defence has stopped working, and the shift is to zero trust

**Next time**: the final session. What kind of computation is it when a machine
"learns"? The story that began with the Turing machine of Lecture 1 arrives at
generative AI and agents.
