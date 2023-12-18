      PROGRAM MKL_SOLVER

!=========================================================================
! Compilation howto 
!
! INTEL:
! module load intel
! ifort MLR.f -o MLR.x -Wl,--start-group \
!             ${MKLROOT}/lib/intel64/libmkl_intel_lp64.a \
!             ${MKLROOT}/lib/intel64/libmkl_core.a \
!             ${MKLROOT}/lib/intel64/libmkl_sequential.a \
!             -Wl,--end-group -lpthread -lm -ldl
!
! GFORTRAN:
! gfortran MLR.f -o MLR.x -lblas -llapack
!  
!=========================================================================
! Input file
!
!  
!  Line 1 : Title
!  Line 2 : NormalizeFlag  can be 0/1/2 
!           NormalizeFlag  = 0 No normalization of data
!           NormalizeFlag  = 1 Normalize all data including LOO system
!           NormalizeFlag  = 2 Normalize all data excluding LOO system
!           NormalizeFlag  = 3 Normalize decritpors only, including LOO system
!           NormalizeFlag  = 4 Normalize decritpors only, excluding LOO system
!  Line 3 : Index of system to be excluded during LOO analysis
!  Line 4 : N of systems (Nsys)
!  Line 5 : N of steric descriptors (Nster)
!  Line 6 : N of electronic descriptors (Nelec)
!  Line 7 : N of points with steric descriptors (Npoint)
!  Line 8 : Nsys Labels identifying the systems
!  Line 9 : Nsys experimental values to be correlated
!
!  Following Nelec lines : Each line Nsys values for a given electronic descriptor
!  Following Npoint lines : Each line R1, R2, and Nster values for each system
!
!=========================================================================
! Following section is revision history
!
!=========================================================================
! 30.03.22 Added labels at the beginning of the electronic descriptor lines
!
!=========================================================================
! 27.11.20 Implemented normalization of descriptors only, not  experimental data:
!          NormalizeFlag = 4  -> Normalize only descriptors, excluding LOO systems
!
!=========================================================================
! 29.08.20 Implemented multiple ways to handle data normalization:
!          NormalizeFlag = 0  -> Do not normalize
!          NormalizeFlag = 1  -> Normalize all data, includng data during LOO
!          NormalizeFlag = 2  -> Normalize only fitted, excluding data during LOO
!          NormalizeFlag = 3  -> Normalize only fitted, prediction based on all normalized data
!
!=========================================================================
! 30.08.20 there can be multiple steric parameters
!          1) nVariables = nElectronics + nSteric ( +1, if IShift = 1)
!          2) combine all the steric terms to Vb
!          3) the new format for volume is R1 R2 V11 V12 V13... V21 V22 V23 ...
!             where, V11 is the first volume term for system 1;
!                    V12 is the second volume term for system 1;
!                    V21 is the first volume term for system 2...
!          4) previously, we read nVariables and let nElectronics = nVariables - 2
!             now, we read two lines for nSteric and nElectronics, respectively
!          5) add one warning message: if standard deviation is too small,
!             normalization can give bad value or even NAN
!
!=========================================================================
! 11.10.19 there can be multiple systems to be skipped
!	for the 3rd line of input file
!	previously, it's index of the one and only one system to be skipped
!	now, it's # of systems to be skipped, index of the systems to be skipped
!	i.e., 3 1 2 3 : three systems to be skipped, and the 1st, 2nd, and 3rd systems to be skipped
!	the new 1 1 is equivalent to the old 1
!
!=========================================================================
! 14.10.19 add NormalizeFlag = 3 option
! in this case, we remove nSkip data; Normalize nSystem - nSkip data; 
! MLR on nSystem - nSkip data; before prediction, we normalize all data again
!
! In this case, sanity check on Normalize Flag is different
! [0, 3] is legal in this case
!
!=========================================================================
! 03.11.19 added more output, which now includes averages and St.Dev data
! Also included Grubbs test to spot problematic cases
!
!=========================================================================
! 13.05.20 added a first line to the input matrix, simple title line
! Title line also written in the output
!=========================================================================


!=========================================================================
! Program source code starts below
!=========================================================================
      IMPLICIT NONE
!=========================================================================
! variables to define the system
!=========================================================================
      Integer :: nSystem                        ! # of systems
      Integer :: nVariables                     ! # of variables
      Integer :: nSteric                        ! # of steric parameters
      Integer :: nElectronics                   ! # of electronic parameters
      Integer :: nPoints                        ! # of points in the steric grid
      Integer :: nMax                           ! # of point with max R2
      Integer :: nSkip                          ! # of systems to be skipped
      Integer :: is                             ! ID of the system to skip for LOO analysis
      Integer :: WK_nSystem                     ! # of systems in work arrays
      Integer :: IShift                         ! key to force fitting through origin
      Integer :: Iwrite                         ! key to write matrix with best R2
!g
      Integer :: Nwork                          ! N of systems fitted
!g

      Integer, Allocatable :: indSkip(:)        ! index of systems to be skipped
      Integer, Allocatable :: iSkip(:)          ! tag indicating a system to be skipped

      Real*8, Allocatable :: Experiments(:)     ! experimental values
      Real*8, Allocatable :: Electronic(:,:)    ! Electronic Parameters
      Real*8, Allocatable :: Vb(:,:,:)          ! % buried volume descriptors
      Real*8, Allocatable :: Rv(:)              ! Vicinal radius
      Real*8, Allocatable :: Rr(:)              ! Remote radius
      Real*8, Allocatable :: Ele_AV(:)         ! Experimental average
      Real*8, Allocatable :: Ele_SD(:)         ! Experimental standard deviation
      Real*8, Allocatable :: Vb_AV(:,:)        ! Experimental average
      Real*8, Allocatable :: Vb_SD(:,:)        ! Experimental standard deviation
      Real*8, Allocatable :: WK_Experiments(:)    ! work array experimental values
      Real*8, Allocatable :: WK_Electronic(:,:)   ! work array Electronic Parameters
      Real*8, Allocatable :: WK_Vb(:,:,:)         ! work array % buried volumes
      Real*8, Allocatable :: Fit(:)         ! Fitted experimental values
      Real*8, Allocatable :: Skip_Ele(:)    ! Skipped system Electronic Parameters
      Real*8, Allocatable :: Skip_Vb(:,:)   ! Skipped system Vbur
      Real*8, Allocatable :: Coef(:)   ! MLR coefficients array

      Real*8              :: Exp_AV         ! Experimental average
      Real*8              :: Exp_SD         ! Experimental standard deviation
!g
      Real*8              :: Dif_AV         ! Average error between fitted and experimental values
      Real*8              :: Dif_SD         ! Standard deviation of error between fitted and experimental values
!g
!     Real*8              :: R2adj          ! Max R2 from scanning nPoints
      Real*8              :: R2max          ! Max R2 from scanning nPoints
c     Real*8              :: Skip_Exp       ! Skipped system experimental value
c     Real*8              :: SER            ! Standard Error on Residuals
c     Real*8              :: SSR            ! S
c     Real*8              :: SSM            ! S
c     Real*8              :: SSE            ! S
c     Real*8              :: tmp, tmp1, tmp2

      Character*150  InputFile                   ! matrix file name
      Character*153  MatrixOutFile               ! matrix output file name with best radius only
      Character*200  Title                       ! matrix title line
      Character*12   Lab_Exp                     ! Experimental data labels
      Character*5000 aString                     ! String input to be parsed for labels

      Character*12,  Allocatable :: Labels(:)                      ! system labels
      Character*12,  Allocatable :: Lab_Ele(:)                     ! Electronic descriptor labels

!=========================================================================
! Operation Flags
!=========================================================================
      Integer :: NormalizeFlag                  ! = 1, normalize the variables
      Integer :: key_warn                       ! = 1, key setting a warn on unreliable fitting

!=========================================================================
! variables for the mkl library
!=========================================================================
      Integer :: m, n, nrhs
      Integer :: lda, ldb
      Integer, Parameter :: lwmax = 100
      Integer :: Info, lwork

      Real*8 :: std, std1, std2
      Real*8 :: Work(lwmax)

      Real*8, Allocatable :: A(:,:)
      Real*8, Allocatable :: B(:,:)

      EXTERNAL         DGELS
      INTRINSIC        INT, MIN


!=========================================================================
! index and varialbes to skip info.
!=========================================================================
      Integer :: i, j, k, l, idum, inan
c     Real*8 :: Rs, Rl, dum1, dum2
      Real*8, Allocatable :: temp(:)


      call getarg(1,InputFile)

!=========================================================================
! Reading the control part
!=========================================================================
      open(101, file=InputFile, status='old')
      read(101,'(a200)')Title
      read(101,*)Iwrite
      read(101,*)NormalizeFlag
      read(101,*)IShift

      read(101,*)nSkip
      Allocate (indSkip(nSkip))
      if (nSkip.gt.0) then
        backspace(101)
        read(101,*)nSkip,indSkip(1:nSkip)     
      endif

      read(101,*)nSystem
      read(101,*)nElectronics
      read(101,*)nSteric
      read(101,*)nPoints

      nVariables = nElectronics + nSteric

!=========================================================================
! you have "nPoints" linear equation systems
! in each system, you have "nSystem" linear equations
!=========================================================================
      lda = nSystem
      ldb = nSystem
      m = nSystem
      nrhs = 1
!=========================================================================
! IShift = 1 : Y = c0 + c1*factor1 + c2*factor2 + ...
! IShift = 0 : Y = c1*factor1 + c2*factor2 + ...
!=========================================================================
		  write(6,*)'  ISh000  ',Ishift, nVariables
      if (IShift .eq. 0) n = nVariables 
      if (IShift .eq. 1) then
         n = nVariables + 1
         nVariables  = nVariables + 1
      endif

		  write(6,*)'  ISh111  ',Ishift, nVariables
!=========================================================================
! Allocate memory
!=========================================================================
      Allocate (Labels(nSystem))
      Allocate (Lab_Ele(nSystem))
      Allocate (Experiments(nSystem))
      Allocate (Rv(nPoints))
      Allocate (Rr(nPoints))
      Allocate (Fit(nSystem))
      Allocate (Vb(nSystem, nPoints,nSteric))
      Allocate (Electronic(nSystem,nElectronics))
      Allocate (temp(nSystem*2))
      Allocate (Coef(nVariables))

      Allocate (Skip_Ele(nElectronics))
      Allocate (Skip_Vb(nPoints,nSteric))

      Allocate (A(lda,n))
      Allocate (B(ldb,nrhs))

      Allocate (WK_Experiments(nSystem))     ! experimental values
      Allocate (WK_Electronic(nSystem,nElectronics))    ! Electronic Parameters
      Allocate (WK_Vb(nSystem,nPoints,nSteric))         ! % of buried volume
      Allocate (Ele_AV(nElectronics))    ! Electronic Parameters
      Allocate (Ele_SD(nElectronics))    ! Electronic Parameters
      Allocate (Vb_AV(npoints,nSteric))  ! Steric Parameters
      Allocate (Vb_SD(npoints,nSteric))  ! Steric Parameters

      Allocate (iSkip(nSystem))  ! Tag to indicate systems to be skipped or not

!=========================================================================
! Reading content
!=========================================================================

      read(101,*)Labels(1:nSystem)                  
      read(101,*)Lab_Exp,(Experiments(j),j=1,nSystem)
      do i = 1, nElectronics
        read(101,*)Lab_Ele(i),(Electronic(j,i),j=1,nSystem)
      enddo

      do i = 1, nPoints
        read(101,*)Rv(i),Rr(i),temp(1:nSystem*nSteric)
        do j = 1, nSystem
          k = (j - 1) * nSteric
          do l = 1, nSteric
            Vb(j, i, l) = temp(k+l)
          enddo
        enddo
      enddo

!=========================================================================
! Write out header and input data
!=========================================================================
      write(6,*)
      write(6,*)'cccccccccccccccccccccccccccccccccccccccccccccccccccccc'
      write(6,*)'c                                                    c'
      write(6,*)'c  MLR program V 1.0                                 c'
      write(6,*)'c                                                    c'
      write(6,*)'c  Release 2020-05-13                                c'
      write(6,*)'c                                                    c'
      write(6,*)'c  Zhen Cao and Luigi Cavallo                        c'
      write(6,*)'c                                                    c'
      write(6,*)'cccccccccccccccccccccccccccccccccccccccccccccccccccccc'
      write(6,*)
      write(6,'(a15,a100)')' Input File : ',InputFile
      write(6,'(a15,a200)')' System     : ',Title
      write(6,*)
      write(6,*)' Number of systems                : ',nSystem
      write(6,*)' Number of Steric descriptors     : ',nSteric
      write(6,*)' Number of Electronic descriptors : ',nElectronics
      write(6,*)' Number of system to be skipped   : ',nSkip
      if (nSkip.gt.0) write(6,*)
     x          ' ID of systems to be skipped      : ',indSkip(1:nSkip)
!     write(6,*)' Normalization Flag               : ',NormalizeFlag
!     
      if (NormalizeFlag.eq.0) then
         write(6,*)' Normalization Flag               : ',
     x   NormalizeFlag, '  No normalization of data'
      endif
!
      if (NormalizeFlag.eq.1) then
          write(6,*)' Normalization Flag               : ',
     x   NormalizeFlag, '  Normalize all data, LOO systems included'
      endif
!
      if (NormalizeFlag.eq.2) then
         write(6,*)' Normalization Flag               : ',
     x   NormalizeFlag, '  Normalize all data, LOO systems excluded'
      endif
!
      if (NormalizeFlag.eq.3) then
         write(6,*)' Normalization Flag               : ',
     x   NormalizeFlag, ' Normalize descritpors, LOO systems included'
      endif
!
      if (NormalizeFlag.eq.4) then
         write(6,*)' Normalization Flag               : ',
     x   NormalizeFlag, ' Normalize descritpors, LOO systems excluded '
      endif
!
      write(6,*)' MLR forced through origin yes/no = 0/1  : ',Ishift
      write(6,*)

!=========================================================================
! Tagging systems to be skipped
!=========================================================================
      do i = 1,nSystem
         iSkip(i) = 0
         do j = 1,nSkip
            if(i.eq.indSkip(j))iSkip(i)=1
         enddo
      enddo

!=========================================================================
! Normalization protocol
! NormalizeFlag = 0  -> Do not normalize
! NormalizeFlag = 1  -> Normalize all data, including data during LOO
! NormalizeFlag = 2  -> Normalize only fitted, excluding data during LOO
! NormalizeFlag = 3  -> Normalize only fitted, prediction based on all normalized data
! Perform sanity check on Normalize Flag
!=========================================================================
      if(NormalizeFlag.lt.0 .or. NormalizeFlag.gt.4) then
         write(6,*)
         write(6,*)" NormalizeFlag =",NormalizeFlag
         write(6,*)" NormalizeFlag key out of allowed range 0-4"
         write(6,*)" Abnormal termination"
         write(6,*)
         stop
      endif
!=========================================================================
! MLR through the origin
! IShift  = 0   -> MLR line forced through the origin 
! IShift  = 1   -> MLR line not forced through the origin 
!
! Perform sanity check on IShift Flag
!=========================================================================
      if(IShift.lt.0 .or. IShift.gt.1) then
         write(6,*)
         write(6,*)" IShift =", IShift
         write(6,*)" IShift key out of allowed range 0-1"
         write(6,*)" Abnormal termination"
         write(6,*)
         stop
      endif
      
!=========================================================================
! Perform sanity check on LOO system
!=========================================================================
      if(nSkip.lt.0 .or. nSkip.gt.nSystem)then
         write(6,*)
         write(6,*)" ID of skipped system out of allowed range"
         write(6,*)" Abnormal termination"
         write(6,*)
         stop
      endif

      if((nSystem - nSkip).lt.nVariables)then
         write(6,*)
         write(6,*)" You remove too many systems"
         write(6,*)" Abnormal termination"
         write(6,*)
         stop
      endif

!=========================================================================
! NormalizeFlag == 0 No normalization 
!=========================================================================
      if(NormalizeFlag.eq.0) then
         call normalization0(Experiments, Electronic, Vb,
     +        Exp_AV, Exp_SD, Ele_AV, Ele_SD, Vb_AV, Vb_SD,
     +        nSystem, nSteric, nElectronics, nPoints) 
      endif

!=========================================================================
! NormalizeFlag == 1 Normalization of all data
!=========================================================================
      if(NormalizeFlag.eq.1) then
         call normalization1(Experiments, Electronic, Vb,
     +        Exp_AV, Exp_SD, Ele_AV, Ele_SD, Vb_AV, Vb_SD,
     +        nSystem, nSteric, nElectronics, nPoints) 
      endif

!=========================================================================
! NormalizeFlag == 2 Normalization of all data, except those skipped
!=========================================================================
      if(NormalizeFlag.eq.2) then
         call normalization2(Experiments, Electronic, Vb,
     +        Exp_AV, Exp_SD, Ele_AV, Ele_SD, Vb_AV, Vb_SD,
     +        nSystem, nSteric, nElectronics, nPoints, iSkip)
      endif

!=========================================================================
! NormalizeFlag == 3 Normalization of descriptors only
!=========================================================================
      if(NormalizeFlag.eq.3) then
         call normalization3(Experiments, Electronic, Vb,
     +        Exp_AV, Exp_SD, Ele_AV, Ele_SD, Vb_AV, Vb_SD,
     +        nSystem, nSteric, nElectronics, nPoints)
      endif

!=========================================================================
! NormalizeFlag == 4 Normalization of descriptors only, except skipped data
!=========================================================================
      if(NormalizeFlag.eq.4) then
         call normalization4(Experiments, Electronic, Vb,
     +        Exp_AV, Exp_SD, Ele_AV, Ele_SD, Vb_AV, Vb_SD,
     +        nSystem, nSteric, nElectronics, nPoints, iSkip)
      endif

!=========================================================================
! Transfer input data into work arrays
! If Nskip > 0 remove this system from analysis
!=========================================================================
      is =  0
      do i = 1, nSystem
        if (nSkip.eq.0) then
          is = is + 1
          do k = 1, nElectronics
            WK_Electronic(is,k) = Electronic(i,k) 
          enddo
        else
          idum = 0
          do j = 1, nSkip
            if (i.eq.indSkip(j)) idum = 1
          enddo
          if (idum.eq.0) then
            is = is + 1
            do k = 1, nElectronics
               WK_Electronic(is,k) = Electronic(i,k) 
            enddo
          endif
        endif
      enddo

      is =  0
      do i = 1, nSystem
        if (nSkip.eq.0) then
          is = is + 1
          do k = 1, nPoints
             do l = 1, nSteric
                WK_Vb(is, k, l) = Vb(i, k, l)
             enddo
          enddo
        else
          idum = 0
          do j = 1, nSkip
            if (i.eq.indSkip(j)) idum = 1
          enddo
          if (idum.eq.0) then
            is = is + 1
            do k = 1, nPoints
               do l = 1, nSteric
                  WK_Vb(is, k, l) = Vb(i, k, l)
               enddo
            enddo
          endif
        endif
      enddo

      is =  0
      do i = 1, nSystem
        if (nSkip.eq.0) then
          is = is + 1
          WK_Experiments(is) = Experiments(i) 
        else
          idum = 0
          do j = 1, nSkip
            if (i.eq.indSkip(j)) idum = 1
          enddo
          if (idum.eq.0) then
              is = is + 1
              WK_Experiments(is) = Experiments(i) 
          endif
        endif
      enddo

      WK_nSystem = nSystem
      if (nSkip.gt.0) WK_nSystem = WK_nSystem - nSkip

!=============================================================================
! warning to check NAN: for sparse matric or some system has identical volume
!=============================================================================
      do j = 1, nPoints
         inan = 0
         do k = 1, nSteric
            if(Vb_AV(j,k).lt.0.00001.or.Vb_SD(j,k).lt.0.00001)then
               inan=1
               write(*,'(a45,a6,i5,a7,i5)')
     x         "Warning: please check buried volume for ", 
     x         "point ", j, "volume ",k
            endif
         enddo
      enddo
!=========================================================================
! solve the linear equation systems
!=========================================================================
      std1 = 0.0
      do i = 1, WK_nSystem
        std1 = std1 + WK_Experiments(i)
        B(i,1) = WK_Experiments(i)
      enddo
      std1 = std1 / dble(WK_nSystem)

      std2 = 0.0
      do i = 1, WK_nSystem
        std2 = std2 + (B(i,1) - std1)**2.
      enddo

      R2Max = 0.0
      nMax = 0
      do i = 1, nPoints
        ! convert variables to A and B
        do j = 1, WK_nSystem
          B(j,1) = WK_Experiments(j)

          if (IShift .eq. 0) then
            do k = 1, nElectronics ! c1...cn-2 for electronics
              A(j,k) = WK_Electronic(j,k)
            enddo
            l = 1 + nElectronics 
          end if
          if (IShift .eq. 1) then
            A(j,1) = 1.0      ! shift: c0
            do k = 1, nElectronics ! c1...cn-2 for electronics
              l  = k  + 1
              A(j,l) = WK_Electronic(j,k)
            enddo
            l = 1 + nElectronics + 1
          end if
          if (IShift .eq. 0)then
            do l = nElectronics + 1, nElectronics + nSteric
              k = l - nElectronics
              A(j,l) = WK_Vb(j,i,k)
            enddo
          endif
          if (Ishift .eq. 1)then
            do l = nElectronics + 2, nElectronics + nSteric + 1
              k = l - nElectronics - 1
              A(j,l) = WK_Vb(j,i,k)
            enddo 
          endif
        enddo

       lwork = -1
       call dgels( 'No transpose', WK_nSystem, N, NRHS, A, LDA, 
     x                B, LDB, WORK, LWORK, INFO)
       lwork = MIN( LWMAX, INT( WORK( 1 ) ) )
       call dgels( 'No transpose', WK_nSystem, N, NRHS, A, LDA, 
     x                B, LDB, WORK, LWORK, INFO )

c      write(6,*)' Coef ', n, Coef
c      write(6,*)' B ', n, B

       do l = 1, n
         Coef(l) = B(l,1)
       enddo
       std = 0.0
       do l = 1, WK_NSystem-n
         std = std + B(n+l,1)*B(n+l,1)
       enddo
c      write(6,'(a10,2i5,9f12.4)')'dbg',WK_NSystem,n,std,std2,
c    x      1.0 - std/std2, Rv(i), Rr(i) 
       if (1.0-std/std2 .gt. R2max) then
         R2max = 1.0-std/std2
         nMax = i
       endif
       write(6,*)"NP " 
     x         ,i,nMax,Rv(i),Rr(i),1.0-std/std2,R2max
     x         ,(B(k,1),k=1,n)
c      write(6,'(a3,2i5,2f6.2,20e12.4)')"NP " 
c    x         ,i,nMax,Rv(i),Rr(i),1.0-std/std2,R2max
c    x         ,(B(k,1),k=1,n)
      enddo

!=========================================================================
! recalculate max R2 point and write out descriptors and coefficients
!=========================================================================
      write(6,*)
      write(6,*)' End calculation'
      R2Max = 0.0
      ! convert variables to A and B
      do j = 1, WK_nSystem
        B(j,1) = WK_Experiments(j)

        if (IShift .eq. 0) then
          do k = 1, nElectronics ! c1...cn-2 for electronics
            A(j,k) = WK_Electronic(j,k)
          enddo
          l = 1 + nElectronics 
        end if

        if (IShift .eq. 1) then
          A(j,1) = 1.0      ! shift: c0
          do k = 1, nElectronics ! c1...cn-2 for electronics
            l  = k  + 1
            A(j,l) = WK_Electronic(j,k)
          enddo
          l = 1 + nElectronics + 1
        end if
        if(IShift .eq. 0) then
          do l = nElectronics + 1, nElectronics + nSteric
            k = l - nElectronics
            A(j,l) = WK_Vb(j,nMax, k)
          enddo
        endif

        if(IShift .eq. 1) then
          do l = nElectronics + 2, nElectronics + nSteric + 1
            k = l - nElectronics - 1
            A(j,l) = WK_Vb(j,nMax, k)
          enddo
        endif

      enddo
      lwork = -1
      call dgels( 'No transpose', WK_nSystem, N, NRHS, A, LDA, 
     x           B, LDB, WORK, LWORK, INFO)
      lwork = MIN( LWMAX, INT( WORK( 1 ) ) )
      call dgels( 'No transpose', WK_nSystem, N, NRHS, A, LDA, 
     x           B, LDB, WORK, LWORK, INFO )
      do l = 1, n
        Coef(l) = B(l,1)
      enddo
      std = 0.0
      do l = 1, m-n
        std = std + B(n+l,1)*B(n+l,1)
      enddo
      R2max = 1.0 - std/std2


!================================================================
! Do sanity check on coefficients.  Values .gt. 10+6 suspicious
! writing warning in output and zero coefficient and fitted data
!================================================================

      key_warn = 0
      do i = 1,n
         if (abs(B(i,1)) .gt. 10e+6)  key_warn = 1 
      enddo

      if (key_warn .eq. 1) then
         write(6,*)
         write(6,*) ' Warning: unreliable coefficients from fitting'
         write(6,'(a6,f8.4,2f5.1,3x,90e18.5)')'Max R2',
     x          1.0 - std/std2, Rv(nMax),Rr(nMax), B(1:n,1)
         write(6,*)' All coefficients will be zeroed'
         write(6,*)
         do i = 1,n
            B(i,1) = 0.0
         enddo
         Rv(nmax) = 0.0
         Rr(nmax) = 0.0
      endif

      write(6,*)
      write(6,*)'      Max-R2, r/Dr pair and coefficients'
      write(6,'(a6,f8.4,2f5.1,3x,90e18.5)')'Max R2',
     x       1.0 - std/std2, Rv(nMax),Rr(nMax), B(1:n,1)


!=========================================================================
! Write out some stuff
!=========================================================================
      write(6,*)
      write(6,*)' Systems fitted & Id of skipped system',nSystem
     x			,indSkip(1:nSkip)
      write(6,*)
      write(6,*)' Input data'
      write(6,*)
      write(6,*)' Experimental data'
      write(6,'(8e12.4)') Experiments(1:nSystem)*Exp_SD+Exp_AV
      write(6,*)
      do i = 1, nElectronics
        write(6,*)' Electronic  Descriptor ', i
        write(6,'(8e12.4)')Electronic(1:nSystem, i)*Ele_SD(i)+Ele_AV(i)
        write(6,*)
      enddo
      do l = 1, nSteric
        write(6,*)' Steric Descriptor ', l
        write(6,'(8e12.4)')(Vb(j,nMax,l)*Vb_SD(nMax,l)+
     x  Vb_AV(nMax,l),j=1,nSystem)
        write(6,*)
      enddo
      write(6,*)
      write(6,*)' Normalized Experimental data'
      write(6,'(10f8.4)') Experiments(1:nSystem)
      write(6,*)
      do i = 1, nElectronics
        write(6,*)' Normalized electronic descriptor ',i
        write(6,'(10f8.4)')Electronic(1:nSystem, i)
      enddo
      write(6,*)
      do l = 1, nSteric
        write(6,*)' Normalized steric descriptor ',l
        write(6,'(10f8.4)')(Vb(j,nMax,l),j=1,nSystem)
      enddo
      write(6,*)

!=========================================================================
! calculate fitted values
!=========================================================================

      if  (IShift.eq.0) then
        do i = 1,nSystem
           Fit(i) =  0.0
           do j =  1,nElectronics
              Fit(i) =  Fit(i)  + B(j,1)*Electronic(i,j)
           end do
           do j = 1, nSteric
             Fit(i) =  Fit(i)  + B(nElectronics+j,1)*Vb(i, nMax, j)
           enddo
        enddo
      endif

      if  (IShift.eq.1) then
        do i = 1,nSystem
           Fit(i) = B(1,1)
           do j =  1,nElectronics
              Fit(i) =  Fit(i)  + B(j+1,1)*Electronic(i,j)
           end do
           do j = 1, nSteric
             Fit(i) =  Fit(i)  + B(nElectronics+j+1,1)*Vb(i, nMax, j)
           enddo
        enddo
      endif

      Dif_AV = 0.0
      Dif_SD = 0.0
      Nwork = 0
      do i = 1,nSystem
        idum = 1
        do j = 1, nSkip
          if (i.eq.indSkip(j)) idum = 0
        enddo
        if (idum.eq.1) then  
           Nwork = Nwork + 1
           Dif_AV = Dif_AV + 
     x     (Exp_AV+Exp_SD*Experiments(i) - Exp_AV+Exp_SD*Fit(i))
        endif
      enddo
      Dif_AV = Dif_AV/float(Nwork)
      do i = 1,nSystem
        idum = 1
        do j = 1, nSkip
          if (i.eq.indSkip(j)) idum = 0
        enddo
        if (idum.eq.1) then
           Dif_SD = Dif_SD +
     x     (Exp_SD*Experiments(i) - Exp_SD*Fit(i) - Dif_AV)*
     x     (Exp_SD*Experiments(i) - Exp_SD*Fit(i) - Dif_AV) 
        endif
      enddo
      Dif_SD = sqrt(Dif_SD/float(Nwork-1))
  
!=========================================================================
! Print out final results
!=========================================================================
      write(6,*)
      write(6,*)' Averages and Standard deviations'
      write(6,'(a20,2f10.4)')' Experimental data ',Exp_AV,Exp_SD
      do i = 1, nElectronics
         write(6,'(a18,i2,2f10.4)')' Elec. Descrip.  ',i,
     x   Ele_AV(i),Ele_SD(i)
      enddo
      do i = 1, nSteric
         write(6,'(a18,i2,2f10.4)')' Steric Descrip. ',i,
     x   Vb_AV(nMax,i),Vb_SD(nMax,i)
      enddo
      write(6,'(a20,2f10.4)')' Fitted - Experim. ', Dif_AV,Dif_SD
      write(6,*)
      write(6,*)'             Normalized  Data', 
     x          '                  Input  Data           Grubbs '
      write(6,*)'    N    Experim.  Fitted     Error',
     x          '    Experim.  Fitted     Error     Test  '
      do i = 1,nSystem
        idum = 1
        do j = 1, nSkip
          if (i.eq.indSkip(j)) idum = 0
        enddo
        if (idum.eq.1) then
           write(6,'(a3,2x,i5,10f10.3)')'Fit',
     x     i,Experiments(i),Fit(i),Fit(i)-Experiments(i),
     x     Exp_AV+Exp_SD*Experiments(i) , Exp_AV+Exp_SD*Fit(i),
     x     Exp_AV+Exp_SD*Fit(i)-Exp_AV-Exp_SD*Experiments(i),
     x     (Exp_SD*Experiments(i)-Exp_SD*Fit(i))/Dif_SD
        endif
      enddo

!=========================================================================
! If no system skipped, and more than one radius examined, print out matrix
! with best radius. 
!=========================================================================
      if (Iwrite.eq.1)  then
         MatrixOutFile='Rm-'//InputFile
         open(102, file=MatrixOutFile, status='unknown')
         write(102,'(a200)')Title
         write(102,*)' 0'                        ! Iwrite 
         write(102,*)NormalizeFlag
         write(102,*)IShift
         write(102,*)nSkip,(indSkip(i),i=1,nSkip)
         write(102,*)nSystem
         write(102,*)nElectronics
         write(102,*)nSteric
         write(102,*)'1'
         write(102,'(12x,*(a12,1x))')(Labels(i),i=1,nSystem)            
         write(102,'(a12,*(e15.6))')
     +        Lab_Exp,(Experiments(1:nSystem)*Exp_SD+Exp_Av)
         do i = 1, nElectronics
            write(102,'(a12,*(e15.6))')Lab_Ele(i),
     +           (Electronic(1:nSystem, i)*Ele_SD(i)+Ele_AV(i))
         enddo
         do j = 1, nSystem
            k = (j - 1) * nSteric
            do l = 1, nSteric
               temp(k+l) = Vb(j, NMax, l)*Vb_SD(NMax,l)+Vb_AV(NMax,l)
            enddo
         enddo
         write(102,'(2f6.2,*(f8.3))')Rv(NMax),Rr(NMax),
     +        (temp(i),i=1,nSteric*nSystem)
      endif
!=========================================================================
! Print out LOO lines if nSkip > 0
!=========================================================================
      if (nSkip.ne.0) then
        write(6,*)
        write(6,*)'  Predicted value of LOO system '
        do j = 1, nSkip
          write(6,'(a3,3x,i3,8e15.5)')
     x    'LOO',indSkip(j),Experiments(indSkip(j)),Fit(indSkip(j)),
     x      Fit(indSkip(j))-Experiments(indSkip(j))
     x     ,Exp_AV+Exp_SD*Experiments(indSkip(j))
     x     ,Exp_AV+Exp_SD*Fit(indSkip(j))
     x     ,Exp_SD*Fit(indSkip(j))-Exp_SD*Experiments(indSkip(j))
        enddo
      endif
      write(6,*)

!=========================================================================
! Print out both training set left out data sequentially
!=========================================================================
      write(6,*)'             Normalized  Data', 
     x          '                  Input  Data'
      write(6,*)'    N    Experim.  Fitted     Error',
     x          '    Experim.  Fitted     Error'
      do i = 1,nSystem
         idum = 1
         do j = 1, nSkip
           if (i.eq.indSkip(j)) idum = 0
         enddo
         if (idum.eq.1)
     x      write(6,'(i3,3x,a12,1x,6e15.5,2x,a3)')
     x      i,Labels(i),Experiments(i),Fit(i),Fit(i)-Experiments(i),
     x      Exp_AV+Exp_SD*Experiments(i) , Exp_AV+Exp_SD*Fit(i),
     x      Exp_AV+Exp_SD*Fit(i)-Exp_AV-Exp_SD*Experiments(i),'Fit'
         if (idum.eq.0)
     x      write(6,'(i3,3x,a12,1x,6e15.5,2x,a3)')
     x      i,Labels(i),Experiments(i),Fit(i),Fit(i)-Experiments(i),
     x      Exp_AV+Exp_SD*Experiments(i) , Exp_AV+Exp_SD*Fit(i),
     x      Exp_AV+Exp_SD*Fit(i)-Exp_AV-Exp_SD*Experiments(i),'Pre'
      enddo

! Do analysis on errors

        do j = 1, WK_nSystem
          B(j,1) = WK_Experiments(j)

          if (IShift .eq. 0) then
            do k = 1, nElectronics ! c1...cn-2 for electronics
              A(j,k) = WK_Electronic(j,k)
            enddo
            l = 1 + nElectronics
          end if
          if (IShift .eq. 1) then
            A(j,1) = 1.0      ! shift: c0
            do k = 1, nElectronics ! c1...cn-2 for electronics
              l  = k  + 1
              A(j,l) = WK_Electronic(j,k)
            enddo
            l = 1 + nElectronics + 1
          end if
          if (IShift .eq. 0)then
            do l = nElectronics + 1, nElectronics + nSteric
              k = l - nElectronics
              A(j,l) = WK_Vb(j,nMax,k)
            enddo
          endif
          if (Ishift .eq. 1)then
            do l = nElectronics + 2, nElectronics + nSteric + 1
              k = l - nElectronics - 1
              A(j,l) = WK_Vb(j,nMax,k)
            enddo
          endif
        enddo

!     call StatAn(nSystem, n, IShift, R2Max,
!    +     Fit, Experiments, A, Coef)

!=========================================================================
! End of program
!=========================================================================
      write(6,*)'  Normal termination'
     
      END

