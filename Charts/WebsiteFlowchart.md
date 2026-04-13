```
@startuml
title Training Platform Flow

start
:Main Site;

if (Login or Sign-up?) then (Sign-up)
  :Enter User Data;
  note right
    Username
    Email
    Password
    Company Code
  end note

  :Create User;

  if (Create Company?) then (yes)
    :Enter Company Data;
    note right
      Company Name
      CVR nr.
      Email
      Admin Account Email
    end note
    :Create Company;
  endif

else (Login)
  :Log in;
endif

:Dashboard;

if (Is User Admin?) then (yes)
  :Admin Dashboard;
  :Employee List;
else (no)
  :Achievements;
  :Leaderboard;
endif

' Training Flow (left side)
:Module List;

if (Select Module?) then (yes)
  :Module #;
  :Static Training;

  if (Paying User?) then (yes)
    :Interactive Training;
    :Quiz / Exam;
  else (no)
    :Back to Module List;
  endif

else (no)
  :Back to Dashboard;
endif

stop

@enduml
```