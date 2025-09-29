import React from 'react';
import { useMutation } from '@tanstack/react-query';
import { useFormik } from 'formik';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
} from 'react-native';
import { theme } from '@/constants/Colors';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { router } from 'expo-router';
import KeyboardView from '@/components/ui/KeyboardView';
import { requestMarketplace } from '@/api/marketplace';
import { marketplaceRequestSchema } from '@/lib/schema';
import Toast from 'react-native-toast-message';
// import { useSmartContract } from '@/hooks/useSmartContract';
import { useAuthorization } from '@/hooks/useAuthorization';
import { PublicKey, SystemProgram } from '@solana/web3.js';
import { BN } from '@coral-xyz/anchor';

export default function RequestMarketplaceScreen() {

  // const program = useSmartContract();
  const { selectedAccount } = useAuthorization();

  const { mutate: mutateRequest, isPending: isRequesting } = useMutation({
    mutationFn: requestMarketplace,
    onSuccess: (res) => {
      console.log('Marketplace Request', res);
      Toast.show({
        type: 'success',
        text1: 'Request submitted successfully',
        text2: 'We will review your request and get back to you soon.',
      });

      // Navigate back or to a success screen
      router.push('/(onboarding)/auth');

    },
    onError: (err: any) => {

      console.log(err?.response?.data)
      // Toast.show({
      //   type: 'error',
      //   text1:      typeof err?.response?.data?.detail === 'string'
      //   ? err?.response?.data?.detail : 'Error submitting request',
      //   text2: 'Please try again later.',
      // });
    },
  });




  const { handleChange, values, errors, handleBlur, handleSubmit, resetForm } =
    useFormik({
      initialValues: {
        universityName: '',
        campusLocation: '',
        adminEmail: '',
        contactEmail: '',
        universityDomain: '',
      },
      validationSchema: marketplaceRequestSchema,
      validateOnBlur: true,
      onSubmit: (values) => {
        mutateRequest({
          university_name: values.universityName,
          campus_location: values.campusLocation,
          admin_email: values.adminEmail,
          contact_email: values.contactEmail,
          university_domain: values.universityDomain,
        });
      },
    });


    

    const handleInitializeMarketplace= async () => {
      
      // if (!program) return;
      // const [marketplacePda] = await PublicKey.findProgramAddress(
      //   [Buffer.from("marketplace")],
      //   program.programId
      // );
    

      // console.log("✅ Marketplace PDA:", marketplacePda);

      // // build & send tx
      // try {
      //   const txSig = await program.methods
      //     .init_marketplace(new BN(5))
      //     .accounts({
      //       marketplace: marketplacePda,
      //       authority: selectedAccount?.publicKey!,
      //       systemProgram: SystemProgram.programId,
      //     })
      //     .rpc();
      
      //   console.log("✅ Marketplace initialized:", txSig);
      // } catch (err: any) {
      //   console.error("❌ Transaction failed:", err);
      
    
      // }
    };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardView style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.title}>Request Marketplace</Text>
          <Text style={styles.subtitle}>
            Request a marketplace for your university campus
          </Text>
        </View>

        <View style={styles.form}>
          <Input
            label="University Name"
            placeholder="Enter university name"
            value={values.universityName}
            onChangeText={handleChange('universityName')}
            error={errors.universityName}
            onBlur={handleBlur('universityName')}
            autoCapitalize="words"
          />

          <Input
            label="Campus Location"
            placeholder="Enter campus location"
            value={values.campusLocation}
            onChangeText={handleChange('campusLocation')}
            error={errors.campusLocation}
            onBlur={handleBlur('campusLocation')}
            autoCapitalize="words"
          />

          <Input
            label="Admin Email"
            placeholder="Enter admin email address"
            value={values.adminEmail}
            onChangeText={handleChange('adminEmail')}
            keyboardType="email-address"
            autoCapitalize="none"
            error={errors.adminEmail}
            onBlur={handleBlur('adminEmail')}
          />

          <Input
            label="Contact Email"
            placeholder="Enter contact email address"
            value={values.contactEmail}
            onChangeText={handleChange('contactEmail')}
            keyboardType="email-address"
            autoCapitalize="none"
            error={errors.contactEmail}
            onBlur={handleBlur('contactEmail')}
          />
          <Input
            label="University Domain"
            placeholder="Enter university domain"
            value={values.universityDomain}
            onChangeText={handleChange('universityDomain')}
            keyboardType="email-address"
            autoCapitalize="none"
            error={errors.universityDomain}
            onBlur={handleBlur('universityDomain')}
          />

          <Button
            title="Submit Request"
            // onPress={handleSubmit}
            onPress={()=> {
              handleSubmit()
            }}
            style={styles.submitButton}
            isLoading={isRequesting}
          />

          <TouchableOpacity
            style={styles.cancelButton}
            onPress={() => {
              resetForm();
              router.back();
            }}
          >
            <Text style={styles.cancelText}>Cancel</Text>
          </TouchableOpacity>
        </View>
      </KeyboardView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.background,
    paddingTop: 50,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 60,
  },
  header: {
    marginBottom: 40,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: theme.text,
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: theme.textMuted,
    textAlign: 'center',
  },
  form: {
    flex: 1,
  },
  submitButton: {
    marginTop: 20,
    marginBottom: 12,
  },
  cancelButton: {
    alignItems: 'center',
    paddingVertical: 16,
  },
  cancelText: {
    fontSize: 14,
    color: theme.textMuted,
  },
});
